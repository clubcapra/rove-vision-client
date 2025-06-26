from PyQt5.QtWidgets import (
  QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout,
  QSlider, QLineEdit, QSizePolicy, QGridLayout
)
from PyQt5.QtCore import Qt

class ControlPanel(QWidget):
    def __init__(self, stream_manager, available_cams):
        super().__init__()

        self.stream_manager = stream_manager
        self.zoom_level = 90  # FOV
        self.current_camera = None

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # Camera buttons
        layout.addWidget(QLabel("Cameras:"))
        self.cam_buttons = {}
        for cam_name in available_cams:
            label = cam_name.capitalize().replace("cam", " Camera").replace("360", "360°")
            btn = self._add_button(layout, label, lambda n=cam_name: self._switch(n))
            self.cam_buttons[cam_name] = btn

        layout.addSpacing(20)
        layout.addWidget(QLabel("Pan/Zoom:"))

        # Notice label
        self.control_notice = QLabel("Controls only available for Dynamic 360° view")
        self.control_notice.setStyleSheet("color: gray; font-style: italic")
        layout.addWidget(self.control_notice)

        self.control_widgets = []

        # Compass-style arrow layout
        arrow_grid = QGridLayout()
        btn_up = QPushButton("↑")
        btn_left = QPushButton("←")
        btn_right = QPushButton("→")
        btn_down = QPushButton("↓")
        btn_reset = QPushButton("Reset")

        for btn in [btn_up, btn_left, btn_right, btn_down, btn_reset]:
            btn.clicked.connect(self._noop)
            self.control_widgets.append(btn)

        arrow_grid.addWidget(btn_up,    0, 1)
        arrow_grid.addWidget(btn_left,  1, 0)
        arrow_grid.addWidget(btn_reset, 1, 1)
        arrow_grid.addWidget(btn_right, 1, 2)
        arrow_grid.addWidget(btn_down,  2, 1)
        layout.addLayout(arrow_grid)

        # Zoom layout
        zoom_layout = QHBoxLayout()
        zoom_out = QPushButton("-")
        zoom_out.clicked.connect(self._noop)
        zoom_in = QPushButton("+")
        zoom_in.clicked.connect(self._noop)
        self.zoom_field = QLineEdit(str(self.zoom_level))
        self.zoom_field.setFixedWidth(50)
        self.zoom_field.returnPressed.connect(self._zoom_field_changed)

        zoom_layout.addWidget(zoom_out)
        zoom_layout.addWidget(self.zoom_field)
        zoom_layout.addWidget(zoom_in)
        layout.addLayout(zoom_layout)
        self.control_widgets.extend([zoom_out, self.zoom_field, zoom_in])

        # Zoom slider
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(30)
        self.zoom_slider.setMaximum(180)
        self.zoom_slider.setValue(self.zoom_level)
        self.zoom_slider.valueChanged.connect(self._zoom_slider_changed)
        layout.addWidget(self.zoom_slider)
        self.control_widgets.append(self.zoom_slider)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.set_camera_context("rearcam")  # Initial state

    def _add_button(self, layout, label, callback):
        btn = QPushButton(label)
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        return btn

    def _switch(self, camera_name):
        self.set_camera_context(camera_name)
        self.stream_manager.switch_stream(camera_name)

    def set_camera_context(self, name):
        self.current_camera = name
        is_dynamic = (name == "dynamic360")
        self._set_controls_enabled(is_dynamic)

    def _set_controls_enabled(self, enabled):
        self.control_notice.setVisible(not enabled)
        for widget in self.control_widgets:
            widget.setEnabled(enabled)

    def _zoom_slider_changed(self, value):
        self.zoom_level = value
        self.zoom_field.setText(str(value))
        self._noop()

    def _zoom_field_changed(self):
        try:
            val = int(self.zoom_field.text())
            if 30 <= val <= 180:
                self.zoom_level = val
                self.zoom_slider.setValue(val)
        except ValueError:
            pass
        self._noop()

    def _noop(self):
        pass  # Placeholder for future implementation