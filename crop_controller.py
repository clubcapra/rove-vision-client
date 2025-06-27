import requests
from stream_manager import STREAMS

class CropController:
    def __init__(self, video_widget, stream_manager):
        self.video_widget = video_widget
        self.stream_manager = stream_manager
        self.zoom_percent = 0  # 0–100%
        self.center_x = None
        self.center_y = None

    def set_zoom_percent(self, val):
        val = max(0, min(100, int(val)))
        self.zoom_percent = val
        self._apply_zoom()

    def zoom_in(self):
        self.set_zoom_percent(self.zoom_percent + 10)

    def zoom_out(self):
        self.set_zoom_percent(self.zoom_percent - 10)

    def reset_crop(self):
        self.zoom_percent = 0
        self.center_x = None
        self.center_y = None
        self._apply_zoom()

    def pan(self, dx, dy):
        stream_name = self.stream_manager.current_stream
        stream_info = STREAMS.get(stream_name)
        if not stream_info:
            return

        width = stream_info["width"]
        height = stream_info["height"]

        if self.center_x is None:
            self.center_x = width // 2
        if self.center_y is None:
            self.center_y = height // 2

        self.center_x += dx * 50
        self.center_y += dy * 50

        # Clamp to image bounds
        self.center_x = max(0, min(width, self.center_x))
        self.center_y = max(0, min(height, self.center_y))

        self._apply_zoom()

    def _apply_zoom(self):
        stream_name = self.stream_manager.current_stream
        if not stream_name:
            print("No active stream")
            return

        stream_info = STREAMS.get(stream_name)
        width = stream_info["width"]
        height = stream_info["height"]

        if self.center_x is None:
            self.center_x = width // 2
        if self.center_y is None:
            self.center_y = height // 2

        max_crop_x = int(width * 0.9 / 2)
        max_crop_y = int(height * 0.9 / 2)
        crop_x = int(max_crop_x * (self.zoom_percent / 100))
        crop_y = int(max_crop_y * (self.zoom_percent / 100))

        # Compute visible window around center
        left = max(0, self.center_x - (width // 2 - crop_x))
        right = max(0, width - (self.center_x + (width // 2 - crop_x)))
        top = max(0, self.center_y - (height // 2 - crop_y))
        bottom = max(0, height - (self.center_y + (height // 2 - crop_y)))

        crop_data = {
            "left": left,
            "right": right,
            "top": top,
            "bottom": bottom
        }

        print(f"Zoom {self.zoom_percent}% @ ({self.center_x},{self.center_y}) → Crop: {crop_data}")
        try:
            response = requests.post("http://jetson-rove.local:8080/crop", json=crop_data)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to send crop request: {e}")
