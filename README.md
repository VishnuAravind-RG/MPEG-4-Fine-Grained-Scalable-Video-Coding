# Video Layer Compression System

This project implements a layered video compression system that separates video into base and enhancement layers for efficient streaming and quality scalability.

## Project Structure

```
.
├── docs/ # Research Paper
├── input/ # Input video files
├── output/ # Output video files
├── src/
│   ├── base_layer.py
│   ├── enhancement_layer.py
│   └── combine_layers.py
```

## Features

- Base layer compression with configurable bitrate
- Enhancement layer processing with residual coding
- Layer combination for different quality outputs
- DCT-based block processing
- YUV color space processing
- FFmpeg integration for final compression

## Requirements

- Python 3.x
- OpenCV (cv2)
- NumPy
- FFmpeg (must be installed and available in system PATH)

## Installation

1. Clone the repository
2. Install Python dependencies:

```sh
pip install opencv-python numpy
```

3. Install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)

## Usage

1. Place your input video in the `input/` directory as `input_video.mp4`

2. Generate the base layer:

```sh
python src/base_layer.py
```

3. Generate the enhancement layer:

```sh
python src/enhancement_layer.py
```

4. Combine the layers:

```sh
python src/combine_layers.py
```

## Output Files

The system generates several output files in the `output/` directory:

- `base_layer.mp4`: Low bitrate base layer
- `enhanced_layer.mp4`: Enhancement layer
- `low_video.mp4`: Base layer quality video
- `high_video.mp4`: High quality enhanced video
- `output_video.mp4`: Final combined video

## Technical Details

### Base Layer

- Uses 8x8 block DCT transform
- Applies coarse quantization (16x16 matrix)
- Targets low bitrate (default 100 kbps)

### Enhancement Layer

- Processes residual between original and base layer
- Uses finer quantization (4x4 matrix)
- Higher bitrate allocation (default 300 kbps)

### Layer Combination

- Supports multiple quality outputs
- Maintains original resolution and framerate
- Provides scalable quality options

## License

This project is open source and available under the MIT License.
