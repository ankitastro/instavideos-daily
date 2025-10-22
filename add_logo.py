#!/usr/bin/env python3
"""
Script to add a logo watermark to the right-hand corner of videos using ffmpeg.
"""

import os
import subprocess
import sys
from pathlib import Path


def add_logo_to_video(video_path, logo_path, output_path, position="top-right", margin=10, logo_scale=0.15):
    """
    Add a logo watermark to a video in the specified corner.

    Args:
        video_path: Path to the input video file
        logo_path: Path to the logo image file
        output_path: Path for the output video file
        position: Position of the logo ("top-right", "top-left", "bottom-right", "bottom-left")
        margin: Margin from the edges in pixels
        logo_scale: Scale of the logo relative to video width (0.15 = 15% of video width)
    """

    # Define position coordinates
    positions = {
        "top-right": f"W-w-{margin}:{margin}",
        "top-left": f"{margin}:{margin}",
        "bottom-right": f"W-w-{margin}:H-h-{margin}",
        "bottom-left": f"{margin}:H-h-{margin}"
    }

    if position not in positions:
        print(f"Invalid position: {position}. Using 'top-right' as default.")
        position = "top-right"

    # Build ffmpeg command
    # The overlay filter: scale logo to logo_scale*video_width, then overlay at position
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-i", logo_path,
        "-filter_complex",
        f"[1:v]scale=iw*{logo_scale}:-1[logo];[0:v][logo]overlay={positions[position]}",
        "-codec:a", "copy",  # Copy audio without re-encoding
        "-y",  # Overwrite output file if it exists
        output_path
    ]

    print(f"Processing: {video_path}")
    print(f"Output: {output_path}")

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ Successfully added logo to {os.path.basename(video_path)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error processing {video_path}:")
        print(f"  {e.stderr}")
        return False


def process_directory(input_dir, logo_path, output_dir=None, position="top-right", margin=10, logo_scale=0.15):
    """
    Process all video files in a directory.

    Args:
        input_dir: Directory containing video files
        logo_path: Path to the logo image file
        output_dir: Output directory (if None, creates 'with_logo' subdirectory)
        position: Position of the logo
        margin: Margin from edges in pixels
        logo_scale: Scale of the logo relative to video width
    """

    input_path = Path(input_dir)
    logo = Path(logo_path)

    if not input_path.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    if not logo.exists():
        print(f"Error: Logo file '{logo_path}' does not exist.")
        return

    # Create output directory
    if output_dir is None:
        output_path = input_path / "with_logo"
    else:
        output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)

    # Supported video extensions
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v', '.webm'}

    # Find all video files
    video_files = [f for f in input_path.iterdir()
                   if f.is_file() and f.suffix.lower() in video_extensions]

    if not video_files:
        print(f"No video files found in '{input_dir}'")
        return

    print(f"Found {len(video_files)} video file(s)")
    print(f"Logo: {logo_path}")
    print(f"Position: {position}")
    print(f"Output directory: {output_path}")
    print("-" * 50)

    success_count = 0
    for video_file in video_files:
        output_file = output_path / video_file.name
        if add_logo_to_video(str(video_file), str(logo), str(output_file), position, margin, logo_scale):
            success_count += 1
        print()

    print("-" * 50)
    print(f"Processed {success_count}/{len(video_files)} videos successfully")


def main():
    """Main function to parse arguments and process videos."""

    if len(sys.argv) < 2:
        print("Usage: python add_logo.py <input_directory> [logo_path] [options]")
        print("\nOptions:")
        print("  --position <pos>    Position: top-right, top-left, bottom-right, bottom-left (default: top-right)")
        print("  --margin <pixels>   Margin from edges in pixels (default: 10)")
        print("  --scale <ratio>     Logo scale relative to video width, e.g., 0.15 for 15% (default: 0.15)")
        print("  --output <dir>      Output directory (default: input_dir/with_logo)")
        print("\nExample:")
        print("  python add_logo.py shambu/blueNeck logo.png --position top-right --margin 20")
        sys.exit(1)

    input_dir = sys.argv[1]

    # Default logo path
    logo_path = "logo.png"
    if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
        logo_path = sys.argv[2]
        arg_start = 3
    else:
        arg_start = 2

    # Parse optional arguments
    position = "top-right"
    margin = 10
    logo_scale = 0.15
    output_dir = None

    i = arg_start
    while i < len(sys.argv):
        if sys.argv[i] == "--position" and i + 1 < len(sys.argv):
            position = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--margin" and i + 1 < len(sys.argv):
            margin = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--scale" and i + 1 < len(sys.argv):
            logo_scale = float(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        else:
            print(f"Unknown argument: {sys.argv[i]}")
            i += 1

    process_directory(input_dir, logo_path, output_dir, position, margin, logo_scale)


if __name__ == "__main__":
    main()
