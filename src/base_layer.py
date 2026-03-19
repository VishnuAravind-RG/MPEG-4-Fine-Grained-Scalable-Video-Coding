import cv2
import numpy as np
import subprocess
import os

def compress_base_layer(input_video_path, output_video_path, bitrate=100):  # 100 kbps
    # Temporary raw video for processing
    temp_raw = "temp_raw.avi"
    
    # Open input video
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video at {input_video_path}")
        return

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Temporary codec #type:ignore

    # Initialize temporary video writer
    out = cv2.VideoWriter(temp_raw, fourcc, fps, (frame_width, frame_height))

    # Quantization matrix for base layer
    quantization_matrix = np.ones((8, 8), dtype=np.float32) * 16

    print("Starting frame processing...")
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to YUV
        frame_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)

        # Process all channels (Y, U, V)
        for channel in range(3):  # 0: Y, 1: U, 2: V
            y_channel = frame_yuv[:, :, channel].astype(np.float32)

            # Apply DCT and quantization to 8x8 blocks
            height, width = y_channel.shape
            for i in range(0, height, 8):
                for j in range(0, width, 8):
                    block = y_channel[i:i+8, j:j+8]
                    if block.shape == (8, 8):
                        dct_block = cv2.dct(block)
                        quantized_block = np.round(dct_block / quantization_matrix)
                        idct_block = cv2.idct(quantized_block * quantization_matrix)
                        y_channel[i:i+8, j:j+8] = idct_block

            # Update the channel in the YUV frame
            frame_yuv[:, :, channel] = y_channel.astype(np.uint8)

        # Reconstruct frame
        reconstructed_frame = cv2.cvtColor(frame_yuv, cv2.COLOR_YUV2BGR)
        out.write(reconstructed_frame)
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"Processed {frame_count} frames...")

    cap.release()
    out.release()
    print(f"Finished processing {frame_count} frames. Converting to MP4...")

    # Use FFmpeg to compress with specified bitrate
    import shutil
    ffmpeg_path = shutil.which('ffmpeg') or r'C:\ffmpeg\bin\ffmpeg.exe'
    cmd = [
        ffmpeg_path, '-i', temp_raw, '-b:v', f'{bitrate}k', '-c:v', 'libx264',
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

    # Remove temporary file
    if os.path.exists(temp_raw):
        os.remove(temp_raw)
    print(f"Base layer compressed video saved as {output_video_path}")

if __name__ == "__main__":
    input_video = "input/input_video.mp4"
    output_video = "output/base_layer.mp4"
    compress_base_layer(input_video, output_video)