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
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

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

def process_single_frame(args):
    """
    Process a single frame to make it circular with transparent background.
    This function is designed to be called in parallel by multiprocessing.

    Args:
        args: Tuple of (frame_data, frame_number, crop_coords, output_size, frames_dir)

    Returns:
        frame_number: The frame number that was processed
    """
    frame_data, frame_number, crop_coords, output_size, frames_dir = args
    left, top, right, bottom = crop_coords

    # Decode frame from bytes
    frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)

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

    # Create circular mask
    mask_pil = Image.new('L', (output_size, output_size), 0)
    draw = ImageDraw.Draw(mask_pil)
    draw.ellipse((0, 0, output_size, output_size), fill=255)

    # Create transparent background
    output_frame = Image.new('RGBA', (output_size, output_size), (0, 0, 0, 0))
    output_frame.paste(pil_img, (0, 0))
    output_frame.putalpha(mask_pil)

    # Save frame as PNG with transparency
    frame_path = os.path.join(frames_dir, f"frame_{frame_number:06d}.png")
    output_frame.save(frame_path, 'PNG')

    return frame_number

def make_video_circular(input_path, output_path, output_size=500, crop_scale=2.5):
    """
    Convert a video to circular format with transparent background.
    Uses face detection on the first frame to determine cropping.

    Args:
        input_path: Path to the input video file
        output_path: Path for the output video file
        output_size: Final output size in pixels (default: 500x500)
        crop_scale: Scale factor for crop radius around face (default: 2.5)
                   Higher values = wider radius, more context around face
                   Lower values = tighter crop, closer to face
                   Typical range: 2.0 (tight) to 4.0 (wide)
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
            # Add padding around face using crop_scale factor
            size = int(face_size * crop_scale)
            print(f"  Using crop scale: {crop_scale}x (radius multiplier)")
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

        # Read all frames into memory and encode them
        print(f"  Reading frames from video...")
        frames_data = []
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        with tqdm(total=total_frames, desc="  Reading frames", unit="frame", ncols=80) as pbar:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                # Encode frame to bytes for passing to worker processes
                _, encoded = cv2.imencode('.jpg', frame)
                frames_data.append(encoded.tobytes())
                pbar.update(1)

        # Release video capture
        cap.release()

        # Prepare arguments for parallel processing
        crop_coords = (left, top, right, bottom)
        process_args = [
            (frame_data, frame_num, crop_coords, output_size, frames_dir)
            for frame_num, frame_data in enumerate(frames_data)
        ]

        # Process frames in parallel with progress bar
        print(f"  Processing {len(frames_data)} frames with {cpu_count()} CPU cores...")

        with Pool(processes=cpu_count()) as pool:
            with tqdm(total=len(frames_data), desc="  Processing frames", unit="frame", ncols=80) as pbar:
                for _ in pool.imap(process_single_frame, process_args):
                    pbar.update(1)

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

def process_directory(input_dir, output_dir=None, output_size=500, crop_scale=2.5):
    """
    Process all video files in a directory.

    Args:
        input_dir: Directory containing video files
        output_dir: Output directory (if None, creates 'output' subdirectory)
        output_size: Final output size in pixels (default: 500x500)
        crop_scale: Scale factor for crop radius around face (default: 2.5)
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
    print(f"Crop scale: {crop_scale}x (radius multiplier)")
    print("-" * 50)

    # Create output directory
    if output_dir:
        out_path = Path(output_dir)
    else:
        out_path = input_path / "output"

    out_path.mkdir(parents=True, exist_ok=True)

    success_count = 0
    for video_file in tqdm(sorted(video_files), desc="Processing videos", unit="video"):
        output_file = out_path / f"{video_file.stem}_circular.mp4"

        print(f"\nProcessing: {video_file.name}")
        if make_video_circular(str(video_file), str(output_file), output_size, crop_scale):
            success_count += 1

    print("-" * 50)
    print(f"Processed {success_count}/{len(video_files)} videos successfully")

def main():
    """Main function to parse arguments and process videos."""

    if len(sys.argv) < 2:
        print("Usage: python make_video_circular.py <input_directory> [output_directory] [OPTIONS]")
        print("\nOptions:")
        print("  --size SIZE         Output resolution in pixels (default: 500)")
        print("  --radius SCALE      Crop radius scale around face (default: 2.5)")
        print("                      Higher = wider radius (more context)")
        print("                      Lower = tighter crop (closer to face)")
        print("                      Typical range: 2.0 (tight) to 4.0 (wide)")
        print("\nExamples:")
        print("  python make_video_circular.py circular_videos")
        print("  python make_video_circular.py circular_videos output --size 1000")
        print("  python make_video_circular.py circular_videos --radius 3.5")
        print("  python make_video_circular.py circular_videos output --size 1000 --radius 3.0")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = None
    output_size = 500
    crop_scale = 2.5

    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--size" and i + 1 < len(sys.argv):
            output_size = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--radius" and i + 1 < len(sys.argv):
            crop_scale = float(sys.argv[i + 1])
            i += 2
        elif not sys.argv[i].startswith("--"):
            output_dir = sys.argv[i]
            i += 1
        else:
            i += 1

    process_directory(input_dir, output_dir, output_size, crop_scale)

if __name__ == "__main__":
    main()
