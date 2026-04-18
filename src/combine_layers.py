import cv2
import numpy as np
import subprocess
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

ENHANCEMENT_QUANT_MATRIX = np.ones((8, 8), dtype=np.float32) * 4

def process_enhancement_frame(args):
    """Process a single frame pair for enhancement layer."""
    base_frame, orig_frame = args

    base_yuv = cv2.cvtColor(base_frame, cv2.COLOR_BGR2YUV).astype(np.float32)
    orig_yuv = cv2.cvtColor(orig_frame, cv2.COLOR_BGR2YUV).astype(np.float32)
    enhanced_yuv = base_yuv.copy()

    for channel in range(3):
        base_ch = base_yuv[:, :, channel]
        orig_ch = orig_yuv[:, :, channel]
        residual = orig_ch - base_ch
        height, width = residual.shape

        pad_h = (8 - height % 8) % 8
        pad_w = (8 - width % 8) % 8
        if pad_h or pad_w:
            residual = np.pad(residual, ((0, pad_h), (0, pad_w)), mode='edge')

        ph, pw = residual.shape
        for i in range(0, ph, 8):
            for j in range(0, pw, 8):
                block = residual[i:i+8, j:j+8]
                dct_block = cv2.dct(block)
                c_max = np.max(np.abs(dct_block))
                if c_max > 0:
                    quantized = np.round(dct_block / ENHANCEMENT_QUANT_MATRIX)
                    residual[i:i+8, j:j+8] = cv2.idct(quantized * ENHANCEMENT_QUANT_MATRIX)

        residual = residual[:height, :width]
        enhanced_ch = np.clip(base_ch + residual, 0, 255)
        enhanced_yuv[:, :, channel] = enhanced_ch

    return cv2.cvtColor(enhanced_yuv.astype(np.uint8), cv2.COLOR_YUV2BGR)

def compress_enhancement_layer(base_video_path, original_video_path, output_video_path, max_bitrate=300):
    temp_raw = "temp_raw_enhanced.avi"

    base_cap = cv2.VideoCapture(base_video_path)
    orig_cap = cv2.VideoCapture(original_video_path)
    if not base_cap.isOpened() or not orig_cap.isOpened():
        print("Error: Could not open videos.")
        return

    frame_width = int(base_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(base_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(base_cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(temp_raw, fourcc, fps, (frame_width, frame_height))

    print("Reading frames...")
    frame_pairs = []
    while True:
        ret_base, base_frame = base_cap.read()
        ret_orig, orig_frame = orig_cap.read()
        if not ret_base or not ret_orig:
            break
        frame_pairs.append((base_frame, orig_frame))
    base_cap.release()
    orig_cap.release()

    print(f"Processing {len(frame_pairs)} frame pairs with {os.cpu_count()} threads...")
    processed = []
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for result in tqdm(executor.map(process_enhancement_frame, frame_pairs), total=len(frame_pairs), desc="Enhancement Layer"):
            processed.append(result)

    for frame in processed:
        out.write(frame)
    out.release()

    print(f"Finished processing {len(processed)} frames. Converting to MP4...")

    ffmpeg_path = shutil.which('ffmpeg') or r'C:\ffmpeg\bin\ffmpeg.exe'
    cmd = [
        ffmpeg_path, '-i', temp_raw,
        '-b:v', f'{max_bitrate}k', '-c:v', 'libx264',
        '-preset', 'medium', '-y', output_video_path
    ]
    try:
        subprocess.run(cmd, check=True, stderr=subprocess.PIPE, text=True)
        print("FFmpeg conversion complete.")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return
    except FileNotFoundError:
        print("Error: FFmpeg not found.")
        return

    if os.path.exists(temp_raw):
        os.remove(temp_raw)
    print(f"Enhancement layer saved as {output_video_path}")

if __name__ == "__main__":
    compress_enhancement_layer("output/base_layer.mp4", "input/input_video.mp4", "output/enhanced_layer.mp4")