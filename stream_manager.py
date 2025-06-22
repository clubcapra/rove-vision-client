import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import threading

STREAMS = {
    "rearcam": "rtsp://192.168.1.104:8554/rearcam",
    "raw360": "rtsp://192.168.1.104:8554/raw360",
    "frontcam": None,
    "dynamic360": None
}

class StreamManager:
    def __init__(self):
        self.pipeline = None
        self.current_stream = None
        self.video_widget = None
        Gst.init(None)

    def switch_stream(self, name):
        uri = STREAMS.get(name)
        if not uri or name == self.current_stream:
            return

        self.stop_stream()

        self.pipeline = Gst.parse_launch(
            f'rtspsrc location={uri} latency=0 ! rtph264depay ! avdec_h264 ! videoconvert ! video/x-raw,format=BGR ! appsink name=sink emit-signals=true sync=false'
        )


        appsink = self.pipeline.get_by_name('sink')
        appsink.connect('new-sample', self.on_new_sample)

        self.pipeline.set_state(Gst.State.PLAYING)
        self.current_stream = name

    def on_new_sample(self, sink):
        sample = sink.emit('pull-sample')
        if sample is None or self.video_widget is None:
            return Gst.FlowReturn.OK

        buf = sample.get_buffer()
        caps = sample.get_caps()
        structure = caps.get_structure(0)
        width = structure.get_value('width')
        success, map_info = buf.map(Gst.MapFlags.READ)

        if success:
            import numpy as np
            import cv2
            size = map_info.size
            height = size // (width * 3)

            frame = np.frombuffer(map_info.data, dtype=np.uint8)
            try:
                frame = frame.reshape((height, width, 3))
                self.video_widget.update_image(frame)
            except ValueError:
                pass  # skip bad frames

            buf.unmap(map_info)

        return Gst.FlowReturn.OK


    def stop_stream(self):
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            self.pipeline = None
            self.current_stream = None
