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
        hbox_videos = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.add(hbox)

        self.stream_manager = StreamManager()
        self.stream_manager_rear = StreamManager()
        self.stream_manager_front = StreamManager()
        self.stream_manager_zedmini = StreamManager()

        # Vertical box to hold the main video widget + two additional widgets stacked vertically
        vbox_videos = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # Main video widget with stream and control panel
        self.video_widget = VideoWidget()

        # Two additional video widgets without controls or streams
        self.video_widget_rear = VideoWidget()
        self.video_widget_front = VideoWidget()
        self.video_widget_zedmini = VideoWidget()

        # Pack the two new widgets below
        hbox_videos.pack_start(self.video_widget_rear, True, True, 0)
        hbox_videos.pack_start(self.video_widget_front, True, True, 0)
        hbox_videos.pack_start(self.video_widget_zedmini, True, True, 0)

        # Pack main video widget on top
        vbox_videos.pack_start(self.video_widget, True, True, 0)
        vbox_videos.pack_start(hbox_videos, True, True, 0)
        
        
        self.stream_manager.switch_stream("insta360", self.video_widget)
        self.stream_manager_rear.switch_stream("rear", self.video_widget_rear)
        self.stream_manager_front.switch_stream("front", self.video_widget_front)
        self.stream_manager_zedmini.switch_stream("zedmini", self.video_widget_zedmini)

        # Control panel on the right for the main video widget only
        control_panel = ControlPanel(self.stream_manager, self.video_widget)

        hbox.pack_start(vbox_videos, True, True, 0)
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
