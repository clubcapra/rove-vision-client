from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

class VideoWidget(QWidget):
    def __init__(self, stream_manager):
        super().__init__()
        self.stream_manager = stream_manager
        self.stream_manager.video_widget = self

        self.label = QLabel("No camera selected")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black; color: white")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_image(self, frame):
        import cv2
        h, w, _ = frame.shape
        side = min(self.label.width(), self.label.height())
        frame = cv2.resize(frame, (side, side), interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, side, side, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qimg))
        self.label.setText("")
