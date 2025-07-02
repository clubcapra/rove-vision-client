#!/usr/bin/env python3
from stream_manager import StreamManager
from control_panel import ControlPanel
from video_widget import VideoWidget

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")
from gi.repository import Gtk, Gst, Gdk, GdkX11, GstVideo

Gst.init(None)

# Constants
CONTROL_PANEL_MIN_WIDTH = 200  # px
CONTROL_PANEL_MIN_HEIGHT = 220  # px

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Rove Vision Viewer")

        # Calculated minimum window size
        min_width = CONTROL_PANEL_MIN_WIDTH * 4  # 3:1 ratio
        min_height = int(CONTROL_PANEL_MIN_HEIGHT / 0.75)
        self.set_default_size(min_width, min_height)
        self.set_size_request(min_width, min_height)

        # Paned layout
        self.paned = Gtk.Paned.new(Gtk.Orientation.VERTICAL)
        self.add(self.paned)

        # Control publisher
        self.control_panel = ControlPanel()
        self.control_panel.set_size_request(-1, CONTROL_PANEL_MIN_HEIGHT)

        # Stream managers
        self.stream_manager_main = StreamManager(self.control_panel)
        self.stream_manager_rear = StreamManager(self.control_panel)

        # Video widgets
        self.main_viewport = VideoWidget(self.stream_manager_main)
        self.secondary_viewport = VideoWidget(self.stream_manager_rear)

        # Sidebar
        # vbox_sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        # vbox_sidebar.set_size_request(CONTROL_PANEL_MIN_WIDTH, -1)
        # vbox_sidebar.pack_start(self.control_panel, False, False, 0)
        # vbox_sidebar.pack_start(self.secondary_viewport, True, True, 0)

        self.paned.pack1(self.main_viewport, resize=True, shrink=False)
        self.paned.pack2(self.secondary_viewport, resize=False, shrink=False)

        # Update divider dynamically on resize
        self.connect("configure-event", self.on_resize)

        self.connect("destroy", self.on_destroy)

    def on_resize(self, widget, event):
        width = self.get_allocated_width()
        self.paned.set_position(int(width * 0.75))  # main = 3/4, sidebar = 1/4

    def on_destroy(self, *args):
        self.stream_manager_main.stop_stream()
        self.stream_manager_rear.stop_stream()
        Gtk.main_quit()


def main():
    win = MainWindow()
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
