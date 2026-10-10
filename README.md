# py_virt_cam_filter

A small Python project that captures a webcam and forwards it as a virtual webcam while applying visual filters and effects.

## Overview

The program reads frames from `/dev/video0`, processes them with OpenCV, and sends the result to a virtual camera on `/dev/video10` via `pyvirtualcam`.

It supports, among others:

- Gaussian blur
- Sigma adjustment
- History / averaging of multiple frames
- Power transform
- Grayscale filter
- Color inversion
- Color tint / filtering
- Color threshold filter
- Live adjustments via keyboard input

## Requirements

- Linux
- Python 3.9+
- OpenCV
- pyvirtualcam
- `v4l2loopback`
- Access to a real camera (for example `/dev/video0`)

## Installation

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install opencv-python pyvirtualcam
```

3. Prepare the virtual camera module:

```bash
chmod +x setup.sh
sudo ./setup.sh
```

The `setup.sh` script loads `v4l2loopback` and creates the virtual camera as `PythonCam`.

## Running the project

Start the project with:

```bash
python gaussian.py
```

The program then starts capturing video and publishes the processed output to the virtual camera.

## Controls

While the program is running, you can adjust settings live using the keyboard:

- `b` – Gaussian blur kernel
- `s` – Gaussian sigma
- `h` – History / frame averaging
- `p` – Power transform
- `g` – Toggle grayscale
- `i` – Toggle color inversion
- `c` – Rotate color filter
- `l` – Custom color
- `t` – Color threshold
- `z` – Invert threshold
- `v` – Pause / resume virtual camera
- `e` or `exit` – Exit

## Project structure

```text
.
├── README.md
├── filter_config.py     # Configuration model and color enum
├── frame_processor.py   # Image processing and filter logic
├── gaussian.py          # Main program with camera and virtual camera loop
├── setup.sh             # Setup for v4l2loopback
```

## Notes

- The project currently uses `/dev/video0` as the default input camera.
- Output is sent to `/dev/video10`.
- The virtual camera must be configured correctly before starting, or the application will not run.
- If you have camera issues, first check whether `v4l2loopback` is loaded and whether `/dev/video10` exists.

