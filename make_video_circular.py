#!/usr/bin/env python3
"""
Script to convert videos to circular format with transparent background.
Uses face detection to center on the face.
"""

import os
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw

def detect_face_in_frame(frame):
    """
    Detect face in a video frame and return face center coordinates and size.

    Args:
        frame: Video frame (numpy array)

    Returns:
        tuple: (center_x, center_y, face_size) or None if no face detected
    """
    # Load the cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Convert to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        # Get the largest face
        largest_face = max(faces, key=lambda face: face[2] * face[3])
        x, y, w, h = largest_face

        # Calculate face center
        center_x = x + w // 2
        center_y = y + h // 2

        # Use larger dimension for face size
        face_size = max(w, h)

        return (center_x, center_y, face_size)

    return None

def make_video_circular(input_path, output_path, output_size=500):
    """
    Convert a video to circular format with transparent background.
    Uses face detection on the first frame to determine cropping.

    Args:
        input_path: Path to the input video file
        output_path: Path for the output video file
        output_size: Final output size in pixels (default: 500x500)
    """
    try:
        # Open the video
        cap = cv2.VideoCapture(input_path)

        if not cap.isOpened():
            print(f"✗ Error: Could not open video {input_path}")
            return False

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"  Video properties: {width}x{height}, {fps} fps, {total_frames} frames")

        # Read first frame to detect face
        ret, first_frame = cap.read()
        if not ret:
            print(f"✗ Error: Could not read first frame from {input_path}")
            cap.release()
            return False

        # Detect face in first frame
        face_info = detect_face_in_frame(first_frame)

        if face_info:
            center_x, center_y, face_size = face_info
            # Add padding around face (2.5x the face size for good framing)
            size = int(face_size * 2.5)
            # Make sure size doesn't exceed video boundaries
            size = min(size, width, height)

            # Calculate crop coordinates centered on face
            left = max(0, center_x - size // 2)
            top = max(0, center_y - size // 2)
            right = min(width, left + size)
            bottom = min(height, top + size)

            # Adjust if we hit boundaries
            if right - left < size:
                if left == 0:
                    right = min(width, size)
                else:
                    left = max(0, width - size)
            if bottom - top < size:
                if top == 0:
                    bottom = min(height, size)
                else:
                    top = max(0, height - size)

            size = min(right - left, bottom - top)
            right = left + size
            bottom = top + size

            print(f"  Face detected - centering on face at ({center_x}, {center_y})")
        else:
            # Fallback to center cropping if no face detected
            size = min(width, height)
            left = (width - size) // 2
            top = (height - size) // 2
            right = left + size
            bottom = top + size
            print(f"  No face detected - using center crop")

        # Reset video to beginning
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # Create temporary directory for frame processing
        import subprocess
        import tempfile

        temp_dir = tempfile.mkdtemp()
        frames_dir = os.path.join(temp_dir, "frames")
        os.makedirs(frames_dir, exist_ok=True)

        # Create circular mask for PIL
        mask_pil = Image.new('L', (output_size, output_size), 0)
        draw = ImageDraw.Draw(mask_pil)
        draw.ellipse((0, 0, output_size, output_size), fill=255)

        # Process each frame
        frame_count = 0
        print(f"  Processing frames with transparency...")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Crop frame to square centered on face
            cropped = frame[top:bottom, left:right]

            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)

            # Convert to PIL Image
            pil_img = Image.fromarray(rgb_frame)

            # Resize to output size
            pil_img = pil_img.resize((output_size, output_size), Image.LANCZOS)

            # Convert to RGBA and apply circular mask
            pil_img = pil_img.convert('RGBA')

            # Create transparent background
            output_frame = Image.new('RGBA', (output_size, output_size), (0, 0, 0, 0))
            output_frame.paste(pil_img, (0, 0))
            output_frame.putalpha(mask_pil)

            # Save frame as PNG with transparency
            frame_path = os.path.join(frames_dir, f"frame_{frame_count:06d}.png")
            output_frame.save(frame_path, 'PNG')

            frame_count += 1
            if frame_count % 30 == 0:
                print(f"  Processed {frame_count}/{total_frames} frames...")

        # Release video capture
        cap.release()

        print(f"  Creating video with transparency...")

        # Use ffmpeg to create video from PNG frames with alpha channel
        # Output as MOV with ProRes 4444 (supports transparency) or WebM with VP9
        output_path_final = str(output_path)

        # Change extension to .mov for transparency support
        if not output_path_final.endswith('.mov') and not output_path_final.endswith('.webm'):
            output_path_final = str(Path(output_path).with_suffix('.mov'))

        # Try MOV with PNG codec first (best transparency support)
        ffmpeg_cmd = [
            'ffmpeg',
            '-framerate', str(fps),
            '-i', os.path.join(frames_dir, 'frame_%06d.png'),
            '-c:v', 'png',
            '-y',
            output_path_final
        ]

        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

        # Clean up temporary directory
        import shutil
        shutil.rmtree(temp_dir)

        if result.returncode == 0:
            print(f"✓ Successfully converted {os.path.basename(input_path)} to circular with transparency")
            print(f"  Output: {output_path_final}")
            return True
        else:
            print(f"✗ Error creating video: {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ Error processing {input_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def process_directory(input_dir, output_dir=None, output_size=500):
    """
    Process all video files in a directory.

    Args:
        input_dir: Directory containing video files
        output_dir: Output directory (if None, creates 'output' subdirectory)
        output_size: Final output size in pixels (default: 500x500)
    """
    input_path = Path(input_dir)

    if not input_path.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    # Supported video extensions
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}

    # Find all video files
    video_files = []
    for ext in video_extensions:
        video_files.extend(input_path.glob(f'*{ext}'))
        video_files.extend(input_path.glob(f'*{ext.upper()}'))

    # Filter out output files
    video_files = [f for f in video_files if 'circular' not in f.stem and 'temp_' not in f.stem]

    if not video_files:
        print(f"No video files found in '{input_dir}'")
        return

    print(f"Found {len(video_files)} video file(s)")
    print(f"Output resolution: {output_size}x{output_size} pixels")
    print("-" * 50)

    # Create output directory
    if output_dir:
        out_path = Path(output_dir)
    else:
        out_path = input_path / "output"

    out_path.mkdir(parents=True, exist_ok=True)

    success_count = 0
    for video_file in sorted(video_files):
        output_file = out_path / f"{video_file.stem}_circular.mp4"

        print(f"\nProcessing: {video_file.name}")
        if make_video_circular(str(video_file), str(output_file), output_size):
            success_count += 1

    print("-" * 50)
    print(f"Processed {success_count}/{len(video_files)} videos successfully")

def main():
    """Main function to parse arguments and process videos."""

    if len(sys.argv) < 2:
        print("Usage: python make_video_circular.py <input_directory> [output_directory] [--size SIZE]")
        print("\nOptions:")
        print("  --size SIZE    Output resolution in pixels (default: 500)")
        print("\nExample:")
        print("  python make_video_circular.py circular_videos")
        print("  python make_video_circular.py circular_videos output --size 500")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = None
    output_size = 500

    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--size" and i + 1 < len(sys.argv):
            output_size = int(sys.argv[i + 1])
            i += 2
        elif not sys.argv[i].startswith("--"):
            output_dir = sys.argv[i]
            i += 1
        else:
            i += 1

    process_directory(input_dir, output_dir, output_size)

if __name__ == "__main__":
    main()
