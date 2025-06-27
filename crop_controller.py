import requests
from stream_manager import STREAMS

class CropController:
    def __init__(self, video_widget, stream_manager):
        self.video_widget = video_widget
        self.stream_manager = stream_manager
        self.zoom_percent = 0  # 0% = no crop, 100% = max crop (1/10 visible)

    def set_zoom_percent(self, val):
        val = max(0, min(100, int(val)))  # Clamp between 0 and 100
        self.zoom_percent = val
        self._apply_zoom()

    def zoom_in(self):
        self.set_zoom_percent(self.zoom_percent + 10)

    def zoom_out(self):
        self.set_zoom_percent(self.zoom_percent - 10)

    def reset_crop(self):
        self.set_zoom_percent(0)

    def _apply_zoom(self):
        stream_name = self.stream_manager.current_stream
        if not stream_name:
            print("No active stream")
            return

        stream_info = STREAMS.get(stream_name)
        if not stream_info:
            print(f"Unknown stream: {stream_name}")
            return

        width = stream_info["width"]
        height = stream_info["height"]

        max_crop_x = int(width * 0.9 / 2)
        max_crop_y = int(height * 0.9 / 2)

        crop_x = int(max_crop_x * (self.zoom_percent / 100))
        crop_y = int(max_crop_y * (self.zoom_percent / 100))

        crop_data = {
            "left": crop_x,
            "right": crop_x,
            "top": crop_y,
            "bottom": crop_y
        }

        print(f"Zoom {self.zoom_percent}% → Cropping: {crop_data}")
        try:
            response = requests.post("http://jetson-rove.local:8080/crop", json=crop_data)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to send crop request: {e}")

    def pan(self, dx, dy):
        print(f"Panning by dx={dx}, dy={dy} (not implemented)")
