
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")
from gi.repository import Gtk, Gst, GdkX11, GstVideo

Gst.init(None)


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