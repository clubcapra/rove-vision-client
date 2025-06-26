#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")
from gi.repository import Gtk, Gst, GdkX11, GstVideo

Gst.init(None)



STREAMS = {
    "rearcam": "rtsp://192.168.1.104:8554/rearcam",
    "raw360": "rtsp://192.168.1.104:8554/raw360",
    "laptopTestCam": "rtsp://localhost:8554/test"
}

class StreamManager:
    def __init__(self):
        self.pipeline = None
        self.current_stream = None
        self.sink = None

    def switch_stream(self, name, video_widget):
        uri = STREAMS.get(name)
        if not uri or name == self.current_stream:
            return

        self.stop_stream()
        print(f"Switching to {name} ({uri})")

        video_widget.show_message(f"Loading {name}...")

        def start_pipeline(_widget):
            pipeline_str = f"""
                rtspsrc location={uri} latency=100 !
                rtph264depay ! avdec_h264 ! videoconvert !
                ximagesink name=videosink sync=false
            """

            self.pipeline = Gst.parse_launch(pipeline_str)
            self.sink = self.pipeline.get_by_name("videosink")

            window = video_widget.drawing_area.get_window()
            if not window:
                print("Error: Drawing area has no window even after realization")
                return

            xid = window.get_xid()
            self.sink.set_window_handle(xid)
            #self.sink.set_property("force-aspect-ratio", True)


            self.pipeline.set_state(Gst.State.PLAYING)
            self.current_stream = name

        # Wait for the drawing area to be realized before starting
        if video_widget.drawing_area.get_realized():
            start_pipeline(video_widget.drawing_area)
        else:
            video_widget.drawing_area.connect("realize", start_pipeline)


    def _on_sync_message(self, bus, msg, video_widget):
        if msg.get_structure() and msg.get_structure().get_name() == "prepare-window-handle":
            def safe_set_handle(_widget):
                window = video_widget.drawing_area.get_window()
                if window:
                    msg.src.set_window_handle(window.get_xid())

            # If realized, set immediately; else defer
            if video_widget.drawing_area.get_realized():
                safe_set_handle(video_widget.drawing_area)
            else:
                video_widget.drawing_area.connect_once("realize", safe_set_handle)



    def stop_stream(self):
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            self.pipeline = None
            self.current_stream = None



