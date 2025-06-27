#!/usr/bin/env python3
import gi
from stream_manager import STREAMS
gi.require_version("Gtk", "3.0")
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")
from gi.repository import Gtk, Gst, GLib, Gdk, GdkX11, GstVideo

Gst.init(None)

class ControlPanel(Gtk.Box):
    def __init__(self, stream_manager, video_widget):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_size_request(250, -1)
        
        self.look_back = False

        self.stream_manager = stream_manager
        
        self.pan_timer = None
        self.pan_direction = None
        
        self.zoom_timer = None
        self.zoom_direction = None


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
        # inner.pack_start(Gtk.Label(label="Cameras:"), False, False, 0)
        # for name in STREAMS:
        #     btn = Gtk.Button(label=name)
        #     btn.connect("clicked", lambda b, n=name: stream_manager.switch_stream(n, video_widget))
        #     inner.pack_start(btn, False, False, 0)

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

        # Enable controls
        for btn in [btn_up, btn_left, btn_right, btn_down, btn_reset]:
            btn.set_sensitive(True)

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
        self.entry = Gtk.Entry()
        self.entry.set_width_chars(5)

        for widget in [btn_minus, btn_plus, self.entry]:
            widget.set_sensitive(True)

        zoom_box.pack_start(btn_minus, False, False, 0)
        zoom_box.pack_start(self.entry, True, True, 0)
        zoom_box.pack_start(btn_plus, False, False, 0)
        inner.pack_start(zoom_box, False, False, 5)

        self.zoom_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1.0, 4.0, 0.1)
        self.zoom_slider.set_digits(1)
        self.zoom_slider.set_sensitive(True)
        inner.pack_start(self.zoom_slider, False, False, 5)

        scroll.add(inner)
        
        self.reflect_zoom()
        
        self.pack_start(scroll, True, True, 0)

        # === Signal handlers ===
        for btn, direction in [
            (btn_left, "left"),
            (btn_right, "right"),
            (btn_up, "up"),
            (btn_down, "down")
        ]:
            btn.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK)
            btn.connect("button-press-event", self.start_pan, direction)
            btn.connect("button-release-event", self.stop_pan)
            
        btn_reset.connect("clicked", self.on_reset)

        for btn, direction in [
            (btn_plus, "in"),
            (btn_minus, "out")
        ]:
            btn.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK)
            btn.connect("button-press-event", self.start_zoom, direction)
            btn.connect("button-release-event", self.stop_zoom)

        self.zoom_slider.connect("value-changed", self.on_slider_zoom)
        
        
        self.entry.connect("activate", self.on_entry)
        self.entry.connect("focus-out-event", self.on_entry)
        
    def on_pan_left(self, _):
        self.stream_manager.set_angle(self.stream_manager.angle - 10 / self.stream_manager.zoom)

    def on_pan_right(self, _):
        self.stream_manager.set_angle(self.stream_manager.angle + 10 / self.stream_manager.zoom)

    def on_pan_up(self, _):
        self.stream_manager.set_top(self.stream_manager.top - 5 / self.stream_manager.zoom)

    def on_pan_down(self, _):
        self.stream_manager.set_top(self.stream_manager.top + 5 / self.stream_manager.zoom)

    def on_reset(self, _):
        self.stream_manager.set_top(50)
        if self.stream_manager.angle % 180 == 0:
            self.look_back = not self.look_back
            
        if self.look_back:
            self.stream_manager.set_angle(180)
        else:
            self.stream_manager.set_angle(0)
        
        self.stream_manager.set_zoom(1)
        self.reflect_zoom()

    def adjust_zoom(self, delta):
        self.stream_manager.set_zoom(self.stream_manager.zoom + delta)
        self.reflect_zoom()

    def on_slider_zoom(self, _):
        self.stream_manager.set_zoom(self.zoom_slider.get_value())
        self.reflect_zoom()
        
    def on_entry(self, widget, *args):
        try:
            value = float(self.entry.get_text())
            value = max(1.0, min(4.0, value))
            self.stream_manager.set_zoom(value)
            self.reflect_zoom()
        except ValueError:
            pass  # ignore invalid input

    def reflect_zoom(self):
        self.zoom_slider.set_value(self.stream_manager.zoom)
        self.entry.set_text(f"{self.stream_manager.zoom}")
        
    def start_pan(self, widget, event, direction):
        if self.pan_timer is None:
            self.pan_direction = direction
            self.pan_timer = GLib.timeout_add(50, self.do_pan)  # 100ms repeat

    def stop_pan(self, widget, event):
        if self.pan_timer:
            GLib.source_remove(self.pan_timer)
            self.pan_timer = None
            self.pan_direction = None

    def do_pan(self):
        if self.pan_direction == "left":
            self.on_pan_left(None)
        elif self.pan_direction == "right":
            self.on_pan_right(None)
        elif self.pan_direction == "up":
            self.on_pan_up(None)
        elif self.pan_direction == "down":
            self.on_pan_down(None)
        return True  # Keep repeating
    
    def start_zoom(self, widget, event, direction):
        if self.zoom_timer is None:
            self.zoom_direction = direction
            self.zoom_timer = GLib.timeout_add(50, self.do_zoom)

    def stop_zoom(self, widget, event):
        if self.zoom_timer:
            GLib.source_remove(self.zoom_timer)
            self.zoom_timer = None
            self.zoom_direction = None

    def do_zoom(self):
        delta = 0.1 if self.zoom_direction == "in" else -0.1
        
        if self.stream_manager.zoom > 5:
            delta = delta * 2
        if self.stream_manager.zoom > 10:
            delta = delta * 5
        self.adjust_zoom(delta)
        return True  # Keep repeating

