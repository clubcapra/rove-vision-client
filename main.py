from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from control_panel import ControlPanel
from video_widget import VideoWidget
from stream_manager import StreamManager, STREAMS
import sys
import os
os.environ["QT_QPA_PLATFORM"] = "xcb"
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Rove Vision Viewer")
    window.resize(1280, 720)

    layout = QHBoxLayout()

    stream_manager = StreamManager()
    video_widget = VideoWidget(stream_manager)

    available_cams = [k for k, v in STREAMS.items() if v is not None]
    control_panel = ControlPanel(stream_manager, available_cams)
    #control_panel = ControlPanel(stream_manager)

    layout.addWidget(video_widget, stretch=4)
    layout.addWidget(control_panel, stretch=1)

    window.setLayout(layout)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
