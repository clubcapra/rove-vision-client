import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")
from gi.repository import Gtk, Gdk, GLib

class ControlPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_size_request(200, 300)

        self.angle = 0      # 0 to 359
        self.top = 50       # 0 to 100
        self.zoom = 50      # 0 to 100

        self.pan_timer = None
        self.pan_direction = None
        self.subscribers = []  # list of StreamManagers

        label = Gtk.Label(label="Controls for Dynamic 360°")
        label.set_margin_top(5)
        self.pack_start(label, False, False, 0)

        # === Pan Grid ===
        grid = Gtk.Grid()
        grid.set_row_spacing(4)
        grid.set_column_spacing(4)

        self.btn_up = Gtk.Button(label="↑")
        self.btn_left = Gtk.Button(label="←")
        self.btn_right = Gtk.Button(label="→")
        self.btn_down = Gtk.Button(label="↓")
        self.btn_n = Gtk.Button(label="N")

        grid.attach(self.btn_up,    1, 0, 1, 1)
        grid.attach(self.btn_left,  0, 1, 1, 1)
        grid.attach(self.btn_n,     1, 1, 1, 1)
        grid.attach(self.btn_right, 2, 1, 1, 1)
        grid.attach(self.btn_down,  1, 2, 1, 1)

        self.pack_start(grid, False, False, 0)

        # === Zoom Slider ===
        self.zoom_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.zoom_slider.set_value(self.zoom)
        self.zoom_slider.connect("value-changed", self.on_zoom_slider)
        self.pack_start(self.zoom_slider, False, False, 0)

        # === NSEW Buttons ===
        box_nsew = Gtk.Box(spacing=4)
        self.btn_w = Gtk.Button(label="W")
        self.btn_s = Gtk.Button(label="S")
        self.btn_e = Gtk.Button(label="E")
        for btn in [self.btn_w, self.btn_s, self.btn_e]:
            btn.set_hexpand(True)
            box_nsew.pack_start(btn, True, True, 0)
        self.pack_start(box_nsew, False, False, 0)

        # === Events ===
        self.btn_up.connect("button-press-event", self.start_pan, "up")
        self.btn_up.connect("button-release-event", self.stop_pan)
        self.btn_down.connect("button-press-event", self.start_pan, "down")
        self.btn_down.connect("button-release-event", self.stop_pan)
        self.btn_left.connect("button-press-event", self.start_pan, "left")
        self.btn_left.connect("button-release-event", self.stop_pan)
        self.btn_right.connect("button-press-event", self.start_pan, "right")
        self.btn_right.connect("button-release-event", self.stop_pan)

        self.btn_n.connect("clicked", lambda w: self.set_direction(0))
        self.btn_w.connect("clicked", lambda w: self.set_direction(270))
        self.btn_s.connect("clicked", lambda w: self.set_direction(180))
        self.btn_e.connect("clicked", lambda w: self.set_direction(90))

    def subscribe(self, stream_manager):
        self.subscribers.append(stream_manager)

    def notify_all(self):
        for sub in self.subscribers:
            sub.on_control_update(self.angle, self.top, self.zoom)

    def set_direction(self, angle_deg):
        self.angle = angle_deg % 360
        self.top = 50
        self.notify_all()

    def on_zoom_slider(self, slider):
        self.zoom = int(slider.get_value())
        self.notify_all()

    def start_pan(self, widget, event, direction):
        if self.pan_timer:
            GLib.source_remove(self.pan_timer)
        self.pan_direction = direction
        self.pan_timer = GLib.timeout_add(50, self.perform_pan)

    def stop_pan(self, widget, event):
        if self.pan_timer:
            GLib.source_remove(self.pan_timer)
            self.pan_timer = None
            self.pan_direction = None

    def perform_pan(self):
        if self.pan_direction == "up":
            self.top = max(0, self.top - 1)
        elif self.pan_direction == "down":
            self.top = min(100, self.top + 1)
        elif self.pan_direction == "left":
            self.angle = (self.angle - 2) % 360
        elif self.pan_direction == "right":
            self.angle = (self.angle + 2) % 360

        self.notify_all()
        return True
    
    def get_current_settings(self):
        return {
            "angle": self.angle,
            "top": self.top,
            "zoom": self.zoom
        }