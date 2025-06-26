#!/usr/bin/env python3
import gi
from stream_manager import STREAMS
gi.require_version("Gtk", "3.0")
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")
from gi.repository import Gtk, Gst, GdkX11, GstVideo

Gst.init(None)

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

