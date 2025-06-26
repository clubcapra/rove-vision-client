#!/usr/bin/env python3
from stream_manager import StreamManager
from control_panel import ControlPanel
from video_widget import VideoWidget

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")
from gi.repository import Gtk, Gst, GdkX11, GstVideo

Gst.init(None)


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
