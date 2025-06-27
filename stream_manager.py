#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")
from gi.repository import Gtk, Gst, GdkX11, GstVideo
from gi.repository import GLib

Gst.init(None)

STREAMS = {
    "rearcam": {
        "width": 1920,
        "height": 1080,
        "url": "rtsp://jetson-rove.local:8554/rearcam"
    },
    "raw360": {
        "width": 2880,
        "height": 1440,
        "url": "rtsp://jetson-rove.local:8554/raw360"
    },
    "laptopTestCam": {
        "width": 2592,
        "height": 1944,
        "url": "rtsp://localhost:8554/test"
    }
}

class StreamManager:
    def __init__(self):
        self.pipeline = None
        self.current_stream = None
        self.sink = None
        self._reconnect_timer = None
        self._video_widget = None

    def switch_stream(self, name, video_widget):
        stream_info = STREAMS.get(name)
        if not stream_info or name == self.current_stream:
            return

        self.stop_stream()
        print(f"Switching to {name} ({stream_info['url']})")
        video_widget.show_message(f"Loading {name}...")
        self._video_widget = video_widget
        self.current_stream = name

        uri = stream_info["url"]
        width = stream_info["width"]
        height = stream_info["height"]

        def start_pipeline(_widget):
            pipeline_str = f"""
                rtspsrc location={uri} latency=100 !
                rtph264depay ! avdec_h264 ! videoconvert ! videoscale !
                ximagesink name=videosink sync=false
            """

            self.pipeline = Gst.parse_launch(pipeline_str)
            self.sink = self.pipeline.get_by_name("videosink")
            self.sink.set_property("force-aspect-ratio", True)

            # Attach to window
            window = video_widget.drawing_area.get_window()
            if not window:
                print("Error: drawing area not ready")
                return
            self.sink.set_window_handle(window.get_xid())
            video_widget.get_toplevel().resize(width, height)

            # Bus watch
            bus = self.pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self._on_bus_message)

            self.pipeline.set_state(Gst.State.PLAYING)

        if video_widget.drawing_area.get_realized():
            start_pipeline(video_widget.drawing_area)
        else:
            video_widget.drawing_area.connect("realize", start_pipeline)

    def _on_bus_message(self, bus, msg):
        t = msg.type
        if t == Gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            print(f"[GStreamer ERROR] {err.message}")
            self._start_reconnect_loop()
        elif t == Gst.MessageType.EOS:
            print("[GStreamer] End of Stream")
            self._start_reconnect_loop()

    def _start_reconnect_loop(self):
        self.stop_stream()
        if self._video_widget:
            self._video_widget.show_message("Stream disconnected. Reconnecting...")

        if self._reconnect_timer:
            GLib.source_remove(self._reconnect_timer)
        self._reconnect_timer = GLib.timeout_add_seconds(1, self._retry_connect)

    def _retry_connect(self):
        print(f"[RETRY] Trying to reconnect to {self.current_stream}")
        if self._video_widget and self.current_stream:
            self.switch_stream(self.current_stream, self._video_widget)
        return False  # Stop this instance of timeout (we re-create it inside switch_stream if needed)

    def stop_stream(self):
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            self.pipeline = None
        if self._reconnect_timer:
            GLib.source_remove(self._reconnect_timer)
            self._reconnect_timer = None
        self.current_stream = None
