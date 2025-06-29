import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")
from gi.repository import Gtk, Gst, GstVideo

from stream_manager import STREAMS

class VideoWidget(Gtk.Box):
    def __init__(self, stream_manager):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.stream_manager = stream_manager

        # Dropdown to select stream
        self.combo = Gtk.ComboBoxText()
        self.combo.append_text("")  # Empty entry = stop stream
        for name in STREAMS.keys():
            self.combo.append_text(name)
        self.combo.set_active(0)
        self.combo.connect("changed", self.on_stream_selected)
        self.pack_start(self.combo, False, False, 0)

        # Drawing area for video
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_vexpand(True)
        self.pack_start(self.drawing_area, True, True, 0)

        # Label for status/info
        self.label = Gtk.Label(label="No stream playing")
        self.pack_start(self.label, False, False, 5)

    def on_stream_selected(self, combo):
        name = combo.get_active_text()
        if name:
            self.stream_manager.switch_stream(name, self)
        else:
            self.stream_manager.stop_stream()
            self.show_message("No stream selected")

    def show_message(self, msg):
        self.label.set_text(msg)
