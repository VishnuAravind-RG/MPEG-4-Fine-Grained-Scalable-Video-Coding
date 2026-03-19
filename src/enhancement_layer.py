import cv2
import numpy as np
import subprocess
import os

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
    fourcc = cv2.VideoWriter_fourcc(*'XVID') #type:ignore

    out = cv2.VideoWriter(temp_raw, fourcc, fps, (frame_width, frame_height))

    # Finer quantization matrix for enhancement (applied to all channels)
    enhancement_quant_matrix = np.ones((8, 8), dtype=np.float32) * 4

    print("Starting enhancement layer processing...")
    frame_count = 0
    while True:
        ret_base, base_frame = base_cap.read()
        ret_orig, orig_frame = orig_cap.read()
        if not ret_base or not ret_orig:
            break

        # Convert to YUV
        base_yuv = cv2.cvtColor(base_frame, cv2.COLOR_BGR2YUV)
        orig_yuv = cv2.cvtColor(orig_frame, cv2.COLOR_BGR2YUV)

        # Process residual for all channels (Y, U, V)
        enhanced_yuv = base_yuv.copy()
        for channel in range(3):  # 0: Y, 1: U, 2: V
            base_channel = base_yuv[:, :, channel].astype(np.float32)
            orig_channel = orig_yuv[:, :, channel].astype(np.float32)
            residual = orig_channel - base_channel

            # Divide into 8x8 blocks and apply DCT to residual
            height, width = residual.shape
            for i in range(0, height, 8):
                for j in range(0, width, 8):
                    block = residual[i:i+8, j:j+8]
                    if block.shape == (8, 8):
                        dct_block = cv2.dct(block)
                        # Simulate bitplane: Find max coeff for number of bitplanes
                        c_max = np.max(np.abs(dct_block))
                        if c_max > 0:
                            n_bp = int(np.floor(np.log2(c_max))) + 1
                            # Simplified embedded quantization: Divide by 2^(n_bp - k) for progressive layers
                            # Here, use finer quant for full enhancement
                            quantized_block = np.round(dct_block / enhancement_quant_matrix)
                            idct_block = cv2.idct(quantized_block * enhancement_quant_matrix)
                            residual[i:i+8, j:j+8] = idct_block

            # Add residual back
            enhanced_channel = np.clip(base_channel + residual, 0, 255).astype(np.uint8)
            enhanced_yuv[:, :, channel] = enhanced_channel

        # Reconstruct frame
        enhanced_frame = cv2.cvtColor(enhanced_yuv, cv2.COLOR_YUV2BGR)
        out.write(enhanced_frame)
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"Processed {frame_count} frames...")

    base_cap.release()
    orig_cap.release()
    out.release()
    print(f"Finished processing {frame_count} frames. Converting to MP4...")

    # Use FFmpeg to compress with specified max bitrate
    import shutil
    ffmpeg_path = shutil.which('ffmpeg') or r'C:\ffmpeg\bin\ffmpeg.exe'
    cmd = [
        ffmpeg_path, '-i', temp_raw, '-b:v', f'{max_bitrate}k', '-c:v', 'libx264',
        '-preset', 'medium', '-y', output_video_path
    ]
    try:
        result = subprocess.run(cmd, check=True, stderr=subprocess.PIPE, text=True)
        print("FFmpeg output:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return
    except FileNotFoundError:
        print("Error: FFmpeg not found. Please install FFmpeg and add it to your PATH.")
        return

    if os.path.exists(temp_raw):
        os.remove(temp_raw)
    print(f"Enhancement layer compressed video saved as {output_video_path}")

if __name__ == "__main__":
    base_video = "output/base_layer.mp4"
    original_video = "input/input_video.mp4"
    enhanced_video = "output/enhanced_layer.mp4"
    compress_enhancement_layer(base_video, original_video, enhanced_video)