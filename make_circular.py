#!/usr/bin/env python3
"""
Script to convert astrologer images to circular format with transparent background.
Uses face detection to ensure faces are centered properly.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw
import cv2
import numpy as np

def detect_face(image_path):
    """
    Detect face in image and return face center coordinates and size.

    Args:
        image_path: Path to the input image file

    Returns:
        tuple: (center_x, center_y, face_size) or None if no face detected
    """
    # Load the cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Read the image
    img_cv = cv2.imread(image_path)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        # Get the largest face
        largest_face = max(faces, key=lambda face: face[2] * face[3])
        x, y, w, h = largest_face

        # Calculate face center
        center_x = x + w // 2
        center_y = y + h // 2

        # Use larger dimension for face size with some padding
        face_size = max(w, h)

        return (center_x, center_y, face_size)

    return None

def make_circular(image_path, output_path, output_size=500):
    """
    Convert an image to circular format with transparent background.
    Uses face detection to center on the face if detected.

    Args:
        image_path: Path to the input image file
        output_path: Path for the output image file
        output_size: Final output size in pixels (default: 500x500)
    """
    try:
        # Open the image
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size

        # Try to detect face
        face_info = detect_face(image_path)

        if face_info:
            center_x, center_y, face_size = face_info
            # Add padding around face (2.5x the face size for good framing)
            size = int(face_size * 2.5)
            # Make sure size doesn't exceed image boundaries
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

            print(f"  Face detected in {os.path.basename(image_path)} - centering on face")
        else:
            # Fallback to center cropping if no face detected
            size = min(width, height)
            left = (width - size) // 2
            top = (height - size) // 2
            right = left + size
            bottom = top + size
            print(f"  No face detected in {os.path.basename(image_path)} - using center crop")

        # Crop to square
        img_square = img.crop((left, top, right, bottom))

        # Resize to standard output size
        img_square = img_square.resize((output_size, output_size), Image.LANCZOS)

        # Create a mask for the circular shape
        mask = Image.new('L', (output_size, output_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, output_size, output_size), fill=255)

        # Create output image with transparent background
        output = Image.new('RGBA', (output_size, output_size), (0, 0, 0, 0))
        output.paste(img_square, (0, 0))
        output.putalpha(mask)

        # Save as PNG to preserve transparency
        output_path = Path(output_path)
        if output_path.suffix.lower() != '.png':
            output_path = output_path.with_suffix('.png')

        output.save(output_path, 'PNG')
        print(f"✓ Successfully converted {os.path.basename(image_path)} to circular")
        return True

    except Exception as e:
        print(f"✗ Error processing {image_path}: {e}")
        return False

def process_directory(input_dir, output_dir=None, output_size=500):
    """
    Process all image files in a directory and its subdirectories.

    Args:
        input_dir: Directory containing image files
        output_dir: Output directory (if None, creates 'circular' subdirectory in each folder)
        output_size: Final output size in pixels (default: 500x500)
    """
    input_path = Path(input_dir)

    if not input_path.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    # Supported image extensions
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}

    # Find all image files recursively
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_path.rglob(f'*{ext}'))
        image_files.extend(input_path.rglob(f'*{ext.upper()}'))

    # Filter out files in output directories
    image_files = [f for f in image_files if 'circular' not in str(f)]

    if not image_files:
        print(f"No image files found in '{input_dir}'")
        return

    print(f"Found {len(image_files)} image file(s)")
    print(f"Output resolution: {output_size}x{output_size} pixels")
    print("-" * 50)

    success_count = 0
    for image_file in sorted(image_files):
        # Determine output path
        if output_dir:
            out_path = Path(output_dir)
            out_path.mkdir(parents=True, exist_ok=True)
            output_file = out_path / (image_file.stem + '_circular.png')
        else:
            # Create 'circular' subdirectory in the same folder as the image
            out_path = image_file.parent / "circular"
            out_path.mkdir(parents=True, exist_ok=True)
            output_file = out_path / (image_file.stem + '_circular.png')

        if make_circular(str(image_file), str(output_file), output_size):
            success_count += 1

    print("-" * 50)
    print(f"Processed {success_count}/{len(image_files)} images successfully")

def main():
    """Main function to parse arguments and process images."""

    if len(sys.argv) < 2:
        print("Usage: python make_circular.py <input_directory> [output_directory] [--size SIZE]")
        print("\nOptions:")
        print("  --size SIZE    Output resolution in pixels (default: 500)")
        print("\nExample:")
        print("  python make_circular.py AstroImages")
        print("  python make_circular.py AstroImages circular_output --size 500")
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
