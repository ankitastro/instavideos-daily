#!/usr/bin/env python3
"""
Script to add a logo watermark to the right-hand corner of images using ffmpeg.
"""

import os
import subprocess
import sys
from pathlib import Path


def add_logo_to_image(image_path, logo_path, output_path, position="top-right", margin=10, logo_scale=0.15):
    """
    Add a logo watermark to an image in the specified corner using ffmpeg.

    Args:
        image_path: Path to the input image file
        logo_path: Path to the logo image file
        output_path: Path for the output image file
        position: Position of the logo ("top-right", "top-left", "bottom-right", "bottom-left")
        margin: Margin from the edges in pixels
        logo_scale: Scale of the logo relative to image width (0.15 = 15% of image width)
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

    # Build ffmpeg command for images
    cmd = [
        "ffmpeg",
        "-i", image_path,
        "-i", logo_path,
        "-filter_complex",
        f"[1:v]scale=iw*{logo_scale}:-1[logo];[0:v][logo]overlay={positions[position]}",
        "-y",  # Overwrite output file if it exists
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ Successfully added logo to {os.path.basename(image_path)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error processing {image_path}:")
        print(f"  {e.stderr}")
        return False


def process_directory(input_dir, logo_path, output_dir=None, position="top-right", margin=10, logo_scale=0.15):
    """
    Process all image files in a directory.

    Args:
        input_dir: Directory containing image files
        logo_path: Path to the logo image file
        output_dir: Output directory (if None, creates 'with_logo' subdirectory)
        position: Position of the logo
        margin: Margin from edges in pixels
        logo_scale: Scale of the logo relative to image width
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

    # Supported image extensions
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}

    # Find all image files
    image_files = [f for f in input_path.iterdir()
                   if f.is_file() and f.suffix.lower() in image_extensions]

    if not image_files:
        print(f"No image files found in '{input_dir}'")
        return

    print(f"Found {len(image_files)} image file(s)")
    print(f"Logo: {logo_path}")
    print(f"Position: {position}")
    print(f"Output directory: {output_path}")
    print("-" * 50)

    success_count = 0
    for image_file in sorted(image_files):
        output_file = output_path / image_file.name
        if add_logo_to_image(str(image_file), str(logo), str(output_file), position, margin, logo_scale):
            success_count += 1

    print("-" * 50)
    print(f"Processed {success_count}/{len(image_files)} images successfully")


def main():
    """Main function to parse arguments and process images."""

    if len(sys.argv) < 2:
        print("Usage: python add_logo_to_images.py <input_directory> [logo_path] [options]")
        print("\nOptions:")
        print("  --position <pos>    Position: top-right, top-left, bottom-right, bottom-left (default: top-right)")
        print("  --margin <pixels>   Margin from edges in pixels (default: 10)")
        print("  --scale <ratio>     Logo scale relative to image width, e.g., 0.15 for 15% (default: 0.15)")
        print("  --output <dir>      Output directory (default: input_dir/with_logo)")
        print("\nExample:")
        print("  python add_logo_to_images.py shambu/blueNeck logo.png --position top-right --margin 20")
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
