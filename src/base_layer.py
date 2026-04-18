import cv2
import numpy as np
import subprocess
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Quantization matrix for base layer
QUANTIZATION_MATRIX = np.ones((8, 8), dtype=np.float32) * 16

def process_frame(frame):
    """Process a single frame with DCT quantization."""
    frame_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV).astype(np.float32)

    for channel in range(3):
        y_channel = frame_yuv[:, :, channel]
        height, width = y_channel.shape

        pad_h = (8 - height % 8) % 8
        pad_w = (8 - width % 8) % 8
        if pad_h or pad_w:
            y_channel = np.pad(y_channel, ((0, pad_h), (0, pad_w)), mode='edge')

        ph, pw = y_channel.shape
        for i in range(0, ph, 8):
            for j in range(0, pw, 8):
                block = y_channel[i:i+8, j:j+8]
                dct_block = cv2.dct(block)
                quantized = np.round(dct_block / QUANTIZATION_MATRIX)
                y_channel[i:i+8, j:j+8] = cv2.idct(quantized * QUANTIZATION_MATRIX)

        frame_yuv[:, :, channel] = np.clip(y_channel[:height, :width], 0, 255)

    return cv2.cvtColor(frame_yuv.astype(np.uint8), cv2.COLOR_YUV2BGR)

def compress_base_layer(input_video_path, output_video_path, bitrate=100):
    temp_raw = "temp_raw.avi"

    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video at {input_video_path}")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(temp_raw, fourcc, fps, (frame_width, frame_height))

    print("Reading frames...")
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()

    print(f"Processing {len(frames)} frames with {os.cpu_count()} threads...")
    processed = []
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for result in tqdm(executor.map(process_frame, frames), total=len(frames), desc="Base Layer"):
            processed.append(result)

    for frame in processed:
        out.write(frame)
    out.release()

    print(f"Finished processing {len(processed)} frames. Converting to MP4...")

    ffmpeg_path = shutil.which('ffmpeg') or r'C:\ffmpeg\bin\ffmpeg.exe'
    cmd = [
        ffmpeg_path, '-i', temp_raw,
        '-b:v', f'{bitrate}k', '-c:v', 'libx264',
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
    print(f"Base layer saved as {output_video_path}")

if __name__ == "__main__":
    compress_base_layer("input/input_video.mp4", "output/base_layer.mp4")