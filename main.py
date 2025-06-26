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


class VideoWidget(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_vexpand(True)
        self.pack_start(self.drawing_area, True, True, 0)
        self.label = Gtk.Label(label="No camera selected")
        self.pack_start(self.label, False, False, 5)

    def show_message(self, msg):
        self.label.set_text(msg)


class ControlPanel(Gtk.Box):
    def __init__(self, stream_manager, video_widget):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_size_request(250, -1)  # fixed width

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_hexpand(False)
        scroll.set_vexpand(True)
        scroll.set_size_request(250, -1)

        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        inner.set_margin_top(10)
        inner.set_margin_bottom(10)
        inner.set_margin_start(10)
        inner.set_margin_end(10)

        # Camera buttons
        inner.pack_start(Gtk.Label(label="Cameras:"), False, False, 0)
        for name in STREAMS:
            btn = Gtk.Button(label=name)
            btn.connect("clicked", lambda b, n=name: stream_manager.switch_stream(n, video_widget))
            inner.pack_start(btn, False, False, 0)

        # Pan/Zoom controls
        inner.pack_start(Gtk.Separator(), False, False, 10)
        inner.pack_start(Gtk.Label(label="Pan/Zoom:"), False, False, 0)
        inner.pack_start(Gtk.Label(label="(Only Dynamic 360° enabled)"), False, False, 0)

        grid = Gtk.Grid()
        btn_up = Gtk.Button(label="↑")
        btn_left = Gtk.Button(label="←")
        btn_right = Gtk.Button(label="→")
        btn_down = Gtk.Button(label="↓")
        btn_reset = Gtk.Button(label="Reset")
        for btn in [btn_up, btn_left, btn_right, btn_down, btn_reset]:
            btn.set_sensitive(False)

        grid.attach(btn_up, 1, 0, 1, 1)
        grid.attach(btn_left, 0, 1, 1, 1)
        grid.attach(btn_reset, 1, 1, 1, 1)
        grid.attach(btn_right, 2, 1, 1, 1)
        grid.attach(btn_down, 1, 2, 1, 1)
        inner.pack_start(grid, False, False, 5)

        # Zoom controls
        zoom_box = Gtk.Box(spacing=4)
        btn_minus = Gtk.Button(label="-")
        btn_plus = Gtk.Button(label="+")
        entry = Gtk.Entry()
        entry.set_text("90")
        entry.set_width_chars(5)
        btn_minus.set_sensitive(False)
        btn_plus.set_sensitive(False)
        entry.set_sensitive(False)
        zoom_box.pack_start(btn_minus, False, False, 0)
        zoom_box.pack_start(entry, True, True, 0)
        zoom_box.pack_start(btn_plus, False, False, 0)
        inner.pack_start(zoom_box, False, False, 5)

        zoom_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 30, 180, 1)
        zoom_slider.set_value(90)
        zoom_slider.set_sensitive(False)
        inner.pack_start(zoom_slider, False, False, 5)

        scroll.add(inner)
        self.pack_start(scroll, True, True, 0)


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Rove Vision Viewer")
        self.set_default_size(1280, 720)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.add(hbox)

        self.stream_manager = StreamManager()
        self.video_widget = VideoWidget()
        control_panel = ControlPanel(self.stream_manager, self.video_widget)

        hbox.pack_start(self.video_widget, True, True, 0)
        hbox.pack_start(control_panel, False, False, 0)

        self.connect("destroy", self.on_destroy)

    def on_destroy(self, *args):
        self.stream_manager.stop_stream()
        Gtk.main_quit()


def main():
    win = MainWindow()
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
