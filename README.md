# 🎬 MPEG-4 Fine-Grained Scalable Video Coding

A layered video compression system implementing **MPEG-4 Fine-Grained Scalable (FGS)** coding — separating video into base and enhancement layers for adaptive streaming and quality scalability.

---

## 📁 Project Structure

```
MPEG-4-Fine-Grained-Scalable-Video-Coding/
├── app.py                  # Streamlit web interface
├── docs/                   # Research paper
├── input/                  # Input video files
├── output/
│   ├── base_layer.mp4
│   ├── enhanced_layer.mp4
│   ├── low_video.mp4
│   ├── high_video.mp4
│   ├── output_video.mp4
│   ├── metrics_report.csv
│   ├── metrics_plot.png
│   └── quality_ladder/     # 100–500 kbps bitrate ladder
└── src/
    ├── base_layer.py
    ├── enhancement_layer.py
    ├── combine_layers.py
    └── metrics.py
```

---

## ✨ Features

- 🔵 **Base Layer Compression** — 8x8 DCT with coarse quantization at 100 kbps
- 🟢 **Enhancement Layer** — Residual coding with finer quantization at 300 kbps
- 📶 **Bitrate Ladder** — 5 quality levels: 100, 200, 300, 400, 500 kbps
- 📊 **Quality Metrics** — PSNR and SSIM analysis with charts and CSV reports
- ⚡ **Multithreaded Processing** — Parallel frame processing using all CPU cores
- 🖥️ **Streamlit Web App** — Browser-based UI for upload, processing, and download

---

## 🛠️ Requirements

- Python 3.x
- OpenCV (`opencv-contrib-python`)
- NumPy
- FFmpeg (installed and added to system PATH)
- Streamlit
- scikit-image
- pandas
- matplotlib
- tqdm

---

## ⚙️ Installation

1. Clone the repository:
```sh
git clone https://github.com/VishnuAravind-RG/MPEG-4-Fine-Grained-Scalable-Video-Coding.git
cd MPEG-4-Fine-Grained-Scalable-Video-Coding
```

2. Create and activate a virtual environment:
```sh
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
```

3. Install Python dependencies:
```sh
pip install opencv-contrib-python numpy streamlit scikit-image pandas matplotlib tqdm
```

4. Install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html) and add it to your PATH.

---

## 🚀 Usage

### Option 1: Web App (Recommended)

```sh
streamlit run app.py
```

Opens at `http://localhost:8501` — upload your video, configure bitrates, run the pipeline, and download outputs directly from the browser.

### Option 2: Command Line

Place your input video at `input/input_video.mp4`, then run:

```sh
python src/base_layer.py
python src/enhancement_layer.py
python src/combine_layers.py
```

Or all at once:
```sh
python src/base_layer.py; python src/enhancement_layer.py; python src/combine_layers.py
```

### Compute Quality Metrics

```sh
python src/metrics.py
```

---

## 📦 Output Files

| File | Description |
|------|-------------|
| `base_layer.mp4` | Low bitrate base layer (100 kbps) |
| `enhanced_layer.mp4` | Enhancement layer (300 kbps) |
| `low_video.mp4` | Base layer quality output |
| `high_video.mp4` | High quality enhanced output |
| `output_video.mp4` | Final combined video |
| `quality_ladder/` | 5 versions at 100–500 kbps |
| `metrics_report.csv` | PSNR/SSIM data per layer |
| `metrics_plot.png` | Quality metrics chart |

---

## 🔬 Technical Details

### Base Layer
- Converts frames from BGR → YUV color space
- Applies **8x8 block DCT transform** to all channels
- Coarse quantization matrix (÷16) — removes fine detail
- Targets **100 kbps** via FFmpeg H.264 encoding

### Enhancement Layer
- Computes **residual** = original frame − base layer frame
- Applies DCT with finer quantization matrix (÷4) on residual
- Adds residual back to recover lost detail
- Targets **300 kbps** via FFmpeg H.264 encoding

### Layer Combination
- Merges base and enhancement layers
- Generates **bitrate ladder**: 100, 200, 300, 400, 500 kbps
- Simulates adaptive bitrate streaming (like YouTube/Netflix)

### Quality Metrics
- **PSNR** (Peak Signal-to-Noise Ratio) — measures pixel-level distortion (>30 dB is good)
- **SSIM** (Structural Similarity Index) — measures perceptual quality (>0.8 is good)
- Per-frame analysis with matplotlib charts

### Performance Optimization
- **Multithreaded frame processing** using `ThreadPoolExecutor`
- Utilizes all available CPU cores automatically
- Progress tracking with `tqdm`

---

## 📊 Sample Metrics

| Layer | Avg PSNR (dB) | Avg SSIM |
|-------|--------------|----------|
| Base Layer | ~28–32 | ~0.75–0.85 |
| Enhanced Layer | ~34–38 | ~0.88–0.95 |
| Final Output | ~34–38 | ~0.88–0.95 |

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).
