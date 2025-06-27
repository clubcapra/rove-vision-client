import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst

import cv2
import numpy as np

Gst.init(None)

STREAMS = {
    "rear": {
        "width": 1920,
        "height": 1080,
        "url": "rtsp://jetson-rove.local:8554/rearcam"
    },
    "insta360": {
        "width": 2880,
        "height": 1440,
        "url": "rtsp://jetson-rove.local:8554/raw360"
    },
}

class StreamManager:
    def __init__(self):
        self.rtsp_pipeline = None
        self.display_pipeline = None
        self.appsink = None
        self.appsrc = None
        self.running = False
        self._framecount = 0
        self.caps_set = False
        self.is_pan_zoom = False

        # Pan/zoom parameters
        self.angle = 0.0  # horizontal pan in degrees
        self.zoom = 1.0   # zoom factor
        self.top = 50.0  # top offset in %
        self.requested_width = 2160  # final output width (you can adjust)

    def switch_stream(self, name, video_widget):
        self.is_pan_zoom = name == "insta360"
        
        stream_info = STREAMS.get(name)
        if not stream_info:
            return

        self.stop_stream()
        print(f"Switching to {name} ({stream_info['url']})")
        video_widget.show_message(f"Loading {name}...")
        
        width = stream_info.get("width")
        height = stream_info.get("height")
        uri = stream_info.get("url")

        # Pipeline to show frames
        self.display_pipeline = Gst.parse_launch(f"""
            appsrc name=customsrc is-live=true block=true format=time !
            videoconvert ! videoscale ! ximagesink name=videosink sync=false
        """)
        self.appsrc = self.display_pipeline.get_by_name("customsrc")
        self.appsrc.set_property("do-timestamp", True)

        self.sink = self.display_pipeline.get_by_name("videosink")
        self.sink.set_property("force-aspect-ratio", True)
        
        area = video_widget.drawing_area
        if area.get_realized():
            self.sink.set_window_handle(area.get_window().get_xid())
        else:
            area.connect("realize", lambda widget: self.sink.set_window_handle(widget.get_window().get_xid()))

        self.display_pipeline.set_state(Gst.State.PLAYING)

        # RTSP frame puller
        self.rtsp_pipeline = Gst.parse_launch(f"""
            rtspsrc location={uri} latency=0 !
            rtph264depay ! avdec_h264 ! videoconvert !
            video/x-raw,format=BGR !
            appsink name=framesink emit-signals=true max-buffers=1 drop=true
        """)
        self.appsink = self.rtsp_pipeline.get_by_name("framesink")
        self.appsink.connect("new-sample", self.on_new_sample)

        self.running = True
        self._framecount = 0
        self.caps_set = False
        self.rtsp_pipeline.set_state(Gst.State.PLAYING)

    def on_new_sample(self, sink):
        sample = sink.emit("pull-sample")
        if sample is None:
            return Gst.FlowReturn.ERROR

        buf = sample.get_buffer()
        caps = sample.get_caps()
        width = caps.get_structure(0).get_value('width')
        height = caps.get_structure(0).get_value('height')

        success, map_info = buf.map(Gst.MapFlags.READ)
        if not success:
            return Gst.FlowReturn.ERROR

        try:
            frame = np.ndarray((height, width, 3), dtype=np.uint8, buffer=map_info.data)
            if self.is_pan_zoom:
                processed = self.apply_pan_zoom(frame)
            else:
                processed = frame
            
            if not self.caps_set:
                if self.is_pan_zoom:
                    caps_str = f"video/x-raw,format=BGR,width={self.requested_width},height={height},framerate=30/1"
                else:
                    caps_str = f"video/x-raw,format=BGR,width={width},height={height},framerate=30/1"
                self.appsrc.set_caps(Gst.Caps.from_string(caps_str))
                self.caps_set = True

            self.push_frame_to_appsrc(processed)

        finally:
            buf.unmap(map_info)

        return Gst.FlowReturn.OK

    def apply_pan_zoom(self, img):
        height = img.shape[0]
        width = img.shape[1]

        crop_width = int(self.requested_width / self.zoom)
        crop_height = int(height / self.zoom)

        start_y = int((height - crop_height) * self.top / 100.0)
        start_x = (width - crop_width) // 2 + int(self.angle * width / 360.0)
        start_x = start_x % width  # wrap around horizontally

        if start_x + crop_width <= width:
            requested_part = img[start_y:start_y + crop_height, start_x:start_x + crop_width]
        else:
            part1 = img[start_y:start_y + crop_height, start_x:]
            part2 = img[start_y:start_y + crop_height, :start_x + crop_width - width]
            requested_part = np.hstack((part1, part2))

        resized = cv2.resize(requested_part, (self.requested_width, height))
        return resized

    def push_frame_to_appsrc(self, frame: np.ndarray):
        if not self.running or self.appsrc is None:
            return

        data = frame.tobytes()
        buf = Gst.Buffer.new_allocate(None, len(data), None)
        buf.fill(0, data)

        buf.pts = Gst.util_uint64_scale(self._framecount, Gst.SECOND, 30)
        buf.duration = Gst.util_uint64_scale(1, Gst.SECOND, 30)
        self._framecount += 1

        ret = self.appsrc.emit("push-buffer", buf)
        if ret != Gst.FlowReturn.OK:
            print(f"[!] Failed to push buffer: {ret}")

    def stop_stream(self):
        self.running = False
        self._framecount = 0
        self.caps_set = False

        if self.rtsp_pipeline:
            self.rtsp_pipeline.set_state(Gst.State.NULL)
            self.rtsp_pipeline = None
        if self.display_pipeline:
            self.display_pipeline.set_state(Gst.State.NULL)
            self.display_pipeline = None

        cv2.destroyAllWindows()

    # Optionally add setters
    def set_zoom(self, zoom: float):
        self.zoom = max(1.0, zoom)

    def set_angle(self, angle: float):
        self.angle = angle % 360
        if self.angle < 0:
            self.angle += 360

    def set_top(self, top_percent: float):
        self.top = max(0.0, min(top_percent, 100.0))

    def set_output_width(self, width: int):
        self.requested_width = max(64, width)
