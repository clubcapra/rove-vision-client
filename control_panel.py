#!/usr/bin/env python3
import gi
from stream_manager import STREAMS
from crop_controller import CropController

gi.require_version("Gtk", "3.0")
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")
from gi.repository import Gtk, Gst, GdkX11, GstVideo

Gst.init(None)

class ControlPanel(Gtk.Box):
    def __init__(self, stream_manager, video_widget):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_size_request(250, -1)

        self.crop_controller = CropController(video_widget, stream_manager)

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
            btn.connect("clicked", lambda b, n=name: self._switch_camera(n, stream_manager, video_widget))
            inner.pack_start(btn, False, False, 0)

        # Pan/Zoom controls
        inner.pack_start(Gtk.Separator(), False, False, 10)
        inner.pack_start(Gtk.Label(label="Pan/Zoom:"), False, False, 0)

        # Pan buttons
        grid = Gtk.Grid()
        btn_up = Gtk.Button(label="↑")
        btn_left = Gtk.Button(label="←")
        btn_right = Gtk.Button(label="→")
        btn_down = Gtk.Button(label="↓")
        btn_reset = Gtk.Button(label="Reset")

        btn_up.connect("clicked", lambda b: self.crop_controller.pan(0, -1))
        btn_left.connect("clicked", lambda b: self.crop_controller.pan(-1, 0))
        btn_right.connect("clicked", lambda b: self.crop_controller.pan(1, 0))
        btn_down.connect("clicked", lambda b: self.crop_controller.pan(0, 1))
        btn_reset.connect("clicked", lambda b: self.crop_controller.reset_crop() or entry.set_text("0") or slider.set_value(0))

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
        entry.set_width_chars(5)
        entry.set_text("0")
        entry.set_sensitive(True)

        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        slider.set_value(0)
        slider.set_digits(0)
        slider.set_sensitive(True)

        def on_plus_clicked(_):
            if self.crop_controller.zoom_percent < 100:
                self.crop_controller.zoom_in()
                entry.set_text(str(self.crop_controller.zoom_percent))
                slider.set_value(self.crop_controller.zoom_percent)

        def on_minus_clicked(_):
            if self.crop_controller.zoom_percent > 0:
                self.crop_controller.zoom_out()
                entry.set_text(str(self.crop_controller.zoom_percent))
                slider.set_value(self.crop_controller.zoom_percent)

        def on_entry_activated(_):
            try:
                val = int(entry.get_text())
                if 0 <= val <= 100:
                    self.crop_controller.set_zoom_percent(val)
                    slider.set_value(val)
                entry.set_text(str(self.crop_controller.zoom_percent))
            except ValueError:
                entry.set_text(str(self.crop_controller.zoom_percent))

        def on_slider_changed(slider_widget):
            val = int(slider_widget.get_value())
            self.crop_controller.set_zoom_percent(val)
            entry.set_text(str(val))

        btn_plus.connect("clicked", on_plus_clicked)
        btn_minus.connect("clicked", on_minus_clicked)
        entry.connect("activate", on_entry_activated)
        slider.connect("value-changed", on_slider_changed)

        zoom_box.pack_start(btn_minus, False, False, 0)
        zoom_box.pack_start(entry, True, True, 0)
        zoom_box.pack_start(btn_plus, False, False, 0)
        inner.pack_start(zoom_box, False, False, 5)
        inner.pack_start(slider, False, False, 5)

        scroll.add(inner)
        self.pack_start(scroll, True, True, 0)

    def _switch_camera(self, name, stream_manager, video_widget):
        stream_manager.switch_stream(name, video_widget)
        self.crop_controller.reset_crop()
