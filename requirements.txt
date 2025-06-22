# RTSP Camera Viewer with Zoom/Pan Controls

A Python GUI application to switch between RTSP camera feeds (one active at a time) and control virtual zoom/pan.

## Features

- RTSP stream switching without consuming multiple feeds
- 4 camera buttons (only Rear and Raw 360 functional)
- Zoom + Pan control UI (to be implemented, will send instructions to server)
- RTSP streams displayed in OpenCV-powered viewer

## Requirements

- Python 3.7+
- `PyQt5`, `opencv-python`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
