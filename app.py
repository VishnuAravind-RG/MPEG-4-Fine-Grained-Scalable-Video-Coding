import streamlit as st
import cv2
import os
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MPEG-4 FGS Video Coder",
    page_icon="🎬",
    layout="wide"
)

# ─── Custom CSS (unchanged) ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'Space Mono', monospace !important;
}

.stApp {
    background: #0a0a0f;
    color: #e8e8f0;
}

.metric-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #0f3460;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 8px 0;
}

.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #e94560;
}

.metric-label {
    font-size: 0.85rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.status-box {
    background: #0f1923;
    border-left: 4px solid #e94560;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    margin: 8px 0;
}

.success-box {
    border-left-color: #00d4aa;
}

.title-accent {
    color: #e94560;
}

div[data-testid="stSidebar"] {
    background: #0f0f1a;
    border-right: 1px solid #1a1a2e;
}

.stButton > button {
    background: linear-gradient(135deg, #e94560, #c62a47);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 12px 24px;
    width: 100%;
    transition: all 0.3s;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(233, 69, 96, 0.4);
}

.stProgress > div > div {
    background: linear-gradient(90deg, #e94560, #ff6b8a);
}
</style>
""", unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown("# 🎬 <span class='title-accent'>MPEG-4</span> Fine-Grained Scalable Video Coder", unsafe_allow_html=True)
st.markdown("*Layered video compression with quality scalability — base + enhancement layer pipeline*")
st.divider()

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.divider()

    base_bitrate = st.slider("Base Layer Bitrate (kbps)", 50, 300, 100, step=10)
    enhancement_bitrate = st.slider("Enhancement Bitrate (kbps)", 100, 800, 300, step=25)

    st.divider()
    st.markdown("### 📊 Quality Ladder")
    generate_ladder = st.checkbox("Generate bitrate ladder", value=True)

    st.divider()
    st.markdown("### 🔬 Metrics")
    compute_metrics = st.checkbox("Compute PSNR / SSIM", value=True)

    st.divider()
    st.markdown("### ℹ️ About")
    st.markdown("""
    This tool implements **MPEG-4 Fine-Grained Scalable** (FGS) video coding:
    - 🔵 **Base layer**: coarse DCT quantization
    - 🟢 **Enhancement**: residual coding
    - 📈 **Metrics**: PSNR & SSIM analysis
    """)

# ─── Upload ─────────────────────────────────────────────────────────────────
st.markdown("## 📁 Upload Video")
uploaded_file = st.file_uploader("Upload your input video (MP4)", type=["mp4", "avi", "mov"])

if uploaded_file:
    # Save to input folder
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    input_path = "input/input_video.mp4"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    # Show video info
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{width}×{height}</div><div class='metric-label'>Resolution</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{fps}</div><div class='metric-label'>FPS</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_frames}</div><div class='metric-label'>Frames</div></div>", unsafe_allow_html=True)
    with col4:
        size_mb = os.path.getsize(input_path) / (1024*1024)
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{size_mb:.1f}MB</div><div class='metric-label'>File Size</div></div>", unsafe_allow_html=True)

    st.divider()

    # ─── Run Pipeline (using subprocess to call working scripts) ────────────
    st.markdown("## 🚀 Run Pipeline")
    if st.button("▶  START COMPRESSION PIPELINE"):

        progress = st.progress(0)
        log = st.empty()

        # Step 1: Base Layer
        log.markdown("<div class='status-box'>⚙️ Step 1/3 — Generating base layer...</div>", unsafe_allow_html=True)
        result = subprocess.run(["python", "src/base_layer.py"], capture_output=True, text=True)
        if result.returncode != 0:
            st.error(f"Base layer failed:\n{result.stderr}")
            st.stop()
        progress.progress(33)

        # Step 2: Enhancement Layer
        log.markdown("<div class='status-box'>⚙️ Step 2/3 — Generating enhancement layer...</div>", unsafe_allow_html=True)
        result = subprocess.run(["python", "src/enhancement_layer.py"], capture_output=True, text=True)
        if result.returncode != 0:
            st.error(f"Enhancement layer failed:\n{result.stderr}")
            st.stop()
        progress.progress(66)

        # Step 3: Combine
        log.markdown("<div class='status-box'>⚙️ Step 3/3 — Combining layers...</div>", unsafe_allow_html=True)
        result = subprocess.run(["python", "src/combine_layers.py"], capture_output=True, text=True)
        if result.returncode != 0:
            st.error(f"Combination failed:\n{result.stderr}")
            st.stop()
        progress.progress(100)

        log.markdown("<div class='status-box success-box'>✅ Pipeline complete!</div>", unsafe_allow_html=True)

        st.divider()

        # ─── Output Files ───────────────────────────────────────────────────
        st.markdown("## 📦 Output Files")
        output_files = {
            "Base Layer (low bitrate)": "output/base_layer.mp4",
            "Enhanced Layer": "output/enhanced_layer.mp4",
            "Low Quality Video": "output/low_video.mp4",
            "High Quality Video": "output/high_video.mp4",
            "Final Output": "output/output_video.mp4",
        }

        cols = st.columns(len(output_files))
        for col, (label, path) in zip(cols, output_files.items()):
            with col:
                if os.path.exists(path):
                    size_kb = os.path.getsize(path) / 1024
                    st.markdown(f"<div class='metric-card'><div class='metric-value'>{size_kb:.0f}KB</div><div class='metric-label'>{label}</div></div>", unsafe_allow_html=True)
                    with open(path, "rb") as f:
                        st.download_button(f"⬇ Download", f.read(), file_name=os.path.basename(path), mime="video/mp4", key=path)

        # ─── Quality Ladder ─────────────────────────────────────────────────
        ladder_dir = "output/quality_ladder"
        if generate_ladder and os.path.exists(ladder_dir):
            st.divider()
            st.markdown("## 📶 Bitrate Ladder")
            ladder_files = sorted([f for f in os.listdir(ladder_dir) if f.endswith(".mp4")])
            for f in ladder_files:
                fpath = os.path.join(ladder_dir, f)
                size_kb = os.path.getsize(fpath) / 1024
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"{f} ({size_kb:.1f} KB)")
                with col2:
                    with open(fpath, "rb") as fp:
                        st.download_button("⬇", fp.read(), file_name=f, mime="video/mp4", key=fpath)

        # ─── Metrics ────────────────────────────────────────────────────────
        if compute_metrics:
            st.divider()
            st.markdown("## 📊 Quality Metrics (PSNR / SSIM)")
            # Run metrics script
            with st.spinner("Computing metrics..."):
                result = subprocess.run(["python", "src/metrics.py"], capture_output=True, text=True)
                if result.returncode != 0:
                    st.warning("Metrics calculation failed. Check if src/metrics.py exists.")
                else:
                    # Load existing CSV if generated
                    csv_path = "output/metrics_report.csv"
                    plot_path = "output/metrics_plot.png"
                    if os.path.exists(csv_path):
                        df = pd.read_csv(csv_path)
                        st.dataframe(df, use_container_width=True)
                    if os.path.exists(plot_path):
                        st.image(plot_path, caption="PSNR & SSIM per frame", use_container_width=True)
                    if os.path.exists(csv_path):
                        with open(csv_path, "rb") as f:
                            st.download_button("⬇ Download Metrics CSV", f.read(), file_name="metrics_report.csv", mime="text/csv")

else:
    st.info("👆 Upload a video file to get started.")
    st.markdown("""
    ### How it works
    1. **Upload** your MP4 video
    2. **Configure** bitrates in the sidebar  
    3. **Run** the compression pipeline
    4. **Download** outputs at any quality level
    5. **Analyze** PSNR/SSIM quality metrics
    """)