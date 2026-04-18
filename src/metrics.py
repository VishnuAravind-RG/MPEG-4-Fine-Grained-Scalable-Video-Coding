import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import pandas as pd
import matplotlib.pyplot as plt
import os

def calculate_metrics(original_path, compressed_path):
    """Calculate PSNR and SSIM between original and compressed video."""
    orig_cap = cv2.VideoCapture(original_path)
    comp_cap = cv2.VideoCapture(compressed_path)

    if not orig_cap.isOpened() or not comp_cap.isOpened():
        print("Error: Could not open videos for metrics calculation.")
        return None

    psnr_values = []
    ssim_values = []
    frame_count = 0

    while True:
        ret_orig, orig_frame = orig_cap.read()
        ret_comp, comp_frame = comp_cap.read()
        if not ret_orig or not ret_comp:
            break

        # Resize comp frame to match original if needed
        if orig_frame.shape != comp_frame.shape:
            comp_frame = cv2.resize(comp_frame, (orig_frame.shape[1], orig_frame.shape[0]))

        # Convert to grayscale for SSIM
        orig_gray = cv2.cvtColor(orig_frame, cv2.COLOR_BGR2GRAY)
        comp_gray = cv2.cvtColor(comp_frame, cv2.COLOR_BGR2GRAY)

        # Calculate PSNR
        p = psnr(orig_frame, comp_frame, data_range=255)
        psnr_values.append(p)

        # Calculate SSIM
        s = ssim(orig_gray, comp_gray, data_range=255)
        ssim_values.append(s)

        frame_count += 1

    orig_cap.release()
    comp_cap.release()

    if not psnr_values:
        return None

    return {
        "avg_psnr": float(np.mean(psnr_values)),
        "min_psnr": float(np.min(psnr_values)),
        "max_psnr": float(np.max(psnr_values)),
        "avg_ssim": float(np.mean(ssim_values)),
        "min_ssim": float(np.min(ssim_values)),
        "max_ssim": float(np.max(ssim_values)),
        "frame_count": frame_count,
        "psnr_values": psnr_values,
        "ssim_values": ssim_values,
    }

def generate_metrics_report(original_path, output_dir="output"):
    """Generate metrics report comparing original vs all output layers."""
    layers = {
        "Base Layer (100kbps)": os.path.join(output_dir, "base_layer.mp4"),
        "Enhanced Layer (300kbps)": os.path.join(output_dir, "enhanced_layer.mp4"),
        "Low Quality": os.path.join(output_dir, "low_video.mp4"),
        "High Quality": os.path.join(output_dir, "high_video.mp4"),
        "Final Output": os.path.join(output_dir, "output_video.mp4"),
    }

    results = []
    all_metrics = {}

    for name, path in layers.items():
        if not os.path.exists(path):
            print(f"Skipping {name} — file not found: {path}")
            continue
        print(f"Calculating metrics for {name}...")
        metrics = calculate_metrics(original_path, path)
        if metrics:
            file_size = os.path.getsize(path) / 1024  # KB
            results.append({
                "Layer": name,
                "Avg PSNR (dB)": round(metrics["avg_psnr"], 2),
                "Min PSNR (dB)": round(metrics["min_psnr"], 2),
                "Avg SSIM": round(metrics["avg_ssim"], 4),
                "Min SSIM": round(metrics["min_ssim"], 4),
                "Frames": metrics["frame_count"],
                "File Size (KB)": round(file_size, 1),
            })
            all_metrics[name] = metrics

    if not results:
        print("No metrics calculated.")
        return None, None

    df = pd.DataFrame(results)
    print("\n=== METRICS REPORT ===")
    print(df.to_string(index=False))

    # Save CSV report
    report_path = os.path.join(output_dir, "metrics_report.csv")
    df.to_csv(report_path, index=False)
    print(f"\nReport saved to {report_path}")

    # Plot PSNR and SSIM charts
    plot_metrics(all_metrics, output_dir)

    return df, all_metrics

def plot_metrics(all_metrics, output_dir="output"):
    """Plot PSNR and SSIM over frames for all layers."""
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle("Video Quality Metrics per Frame", fontsize=14, fontweight="bold")

    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6"]

    for idx, (name, metrics) in enumerate(all_metrics.items()):
        color = colors[idx % len(colors)]
        frames = range(len(metrics["psnr_values"]))

        axes[0].plot(frames, metrics["psnr_values"], label=name, color=color, linewidth=1.5)
        axes[1].plot(frames, metrics["ssim_values"], label=name, color=color, linewidth=1.5)

    axes[0].set_title("PSNR (higher is better)")
    axes[0].set_ylabel("PSNR (dB)")
    axes[0].set_xlabel("Frame")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].set_title("SSIM (higher is better, max=1.0)")
    axes[1].set_ylabel("SSIM")
    axes[1].set_xlabel("Frame")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plot_path = os.path.join(output_dir, "metrics_plot.png")
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Metrics plot saved to {plot_path}")

if __name__ == "__main__":
    original = "input/input_video.mp4"
    generate_metrics_report(original)