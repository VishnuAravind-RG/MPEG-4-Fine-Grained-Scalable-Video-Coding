import cv2

def combine_layers(base_video_path, enhanced_video_path, low_output_path, high_output_path, output_video_path):
    # Open base and enhanced videos
    base_cap = cv2.VideoCapture(base_video_path)
    enhanced_cap = cv2.VideoCapture(enhanced_video_path)
    if not base_cap.isOpened() or not enhanced_cap.isOpened():
        print("Error: Could not open videos.")
        return

    # Get video properties
    frame_width = int(base_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(base_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(base_cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # Initialize output video writers
    low_out = cv2.VideoWriter(low_output_path, fourcc, fps, (frame_width, frame_height))
    high_out = cv2.VideoWriter(high_output_path, fourcc, fps, (frame_width, frame_height))
    final_out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    print("Combining layers...")
    frame_count = 0
    while True:
        ret_base, base_frame = base_cap.read()
        ret_enhanced, enhanced_frame = enhanced_cap.read()
        if not ret_base or not ret_enhanced:
            break

        # Write to outputs
        low_out.write(base_frame)
        high_out.write(enhanced_frame)
        final_out.write(enhanced_frame)  # Always save enhanced as output_video.mp4
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"Processed {frame_count} frames...")

    base_cap.release()
    enhanced_cap.release()
    low_out.release()
    high_out.release()
    final_out.release()
    print(f"Finished processing {frame_count} frames.")

    print(f"Low-quality video saved as {low_output_path}")
    print(f"High-quality video saved as {high_output_path}")
    print(f"Final enhanced video saved as {output_video_path}")

if __name__ == "__main__":
    base_video = "output/base_layer.mp4"
    enhanced_video = "output/enhanced_layer.mp4"
    low_output = "output/low_video.mp4"
    high_output = "output/high_video.mp4"
    output_video = "output/output_video.mp4"
    combine_layers(base_video, enhanced_video, low_output, high_output, output_video)