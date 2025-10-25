#!/usr/bin/env python3
"""
Script to convert video files to GIF format with customizable quality and size.
"""

import os
import sys
import subprocess
from pathlib import Path


def convert_video_to_gif(video_path, output_path=None, fps=10, width=None, quality='medium', start_time=None, duration=None):
    """
    Convert a video file to GIF format.

    Args:
        video_path: Path to the input video file
        output_path: Path for the output GIF file (optional)
        fps: Frames per second for the GIF (default: 10)
        width: Width in pixels (height auto-calculated to maintain aspect ratio)
        quality: Quality level - 'low', 'medium', 'high' (affects color palette)
        start_time: Start time in seconds (optional, for extracting segment)
        duration: Duration in seconds (optional, for extracting segment)

    Returns:
        bool: True if successful, False otherwise
    """
    video_path = Path(video_path)

    if not video_path.exists():
        print(f"✗ Error: Video file '{video_path}' does not exist.")
        return False

    # Determine output path
    if output_path is None:
        output_path = video_path.with_suffix('.gif')
    else:
        output_path = Path(output_path)

    # Quality settings (palette generation)
    quality_settings = {
        'low': {'colors': 128, 'dither': 'bayer:bayer_scale=3'},
        'medium': {'colors': 256, 'dither': 'bayer:bayer_scale=5'},
        'high': {'colors': 256, 'dither': 'floyd_steinberg'}
    }

    if quality not in quality_settings:
        print(f"Warning: Invalid quality '{quality}'. Using 'medium'.")
        quality = 'medium'

    settings = quality_settings[quality]

    print(f"Converting video to GIF: {video_path.name}")
    print(f"Output: {output_path}")
    print(f"Settings: {fps} fps, Quality: {quality}")
    if width:
        print(f"Width: {width}px (height: auto)")
    if start_time is not None:
        print(f"Start time: {start_time}s")
    if duration is not None:
        print(f"Duration: {duration}s")

    try:
        # Build filter complex for high-quality GIF conversion
        # This uses a two-pass approach: generate palette, then create GIF

        # Scale filter
        if width:
            scale_filter = f"scale={width}:-1:flags=lanczos"
        else:
            scale_filter = "scale=iw:ih:flags=lanczos"

        # Input options
        input_options = ['-i', str(video_path)]

        # Add start time and duration if specified
        if start_time is not None:
            input_options.insert(0, '-ss')
            input_options.insert(1, str(start_time))

        if duration is not None:
            input_options.insert(0, '-t')
            input_options.insert(1, str(duration))

        # Step 1: Generate color palette
        palette_path = video_path.parent / f"palette_{video_path.stem}.png"

        palette_filter = f"{scale_filter},fps={fps},palettegen=max_colors={settings['colors']}:stats_mode=diff"

        palette_cmd = [
            'ffmpeg',
            *input_options,
            '-vf', palette_filter,
            '-y',
            str(palette_path)
        ]

        print("Generating color palette...")
        result = subprocess.run(palette_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"✗ Error generating palette:")
            print(result.stderr)
            return False

        # Step 2: Create GIF using the palette
        gif_filter = f"{scale_filter},fps={fps}[x];[x][1:v]paletteuse=dither={settings['dither']}"

        gif_cmd = [
            'ffmpeg',
            *input_options,
            '-i', str(palette_path),
            '-filter_complex', gif_filter,
            '-loop', '0',  # Loop forever
            '-y',
            str(output_path)
        ]

        print("Creating GIF...")
        result = subprocess.run(gif_cmd, capture_output=True, text=True)

        # Clean up palette file
        if palette_path.exists():
            os.remove(palette_path)

        if result.returncode == 0:
            file_size = output_path.stat().st_size / (1024 * 1024)  # Size in MB
            print(f"✓ Successfully created GIF: {output_path.name} ({file_size:.2f} MB)")
            return True
        else:
            print(f"✗ Error creating GIF:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        # Clean up palette file if it exists
        palette_path = video_path.parent / f"palette_{video_path.stem}.png"
        if palette_path.exists():
            os.remove(palette_path)
        return False


def process_directory(input_dir, output_dir=None, fps=10, width=None, quality='medium'):
    """
    Convert all video files in a directory to GIF.

    Args:
        input_dir: Directory containing video files
        output_dir: Output directory (if None, saves in same directory as video)
        fps: Frames per second for GIFs
        width: Width in pixels
        quality: Quality level
    """
    input_path = Path(input_dir)

    if not input_path.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    # Supported video extensions
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}

    # Find all video files
    video_files = []
    for ext in video_extensions:
        video_files.extend(input_path.glob(f'*{ext}'))
        video_files.extend(input_path.glob(f'*{ext.upper()}'))

    if not video_files:
        print(f"No video files found in '{input_dir}'")
        return

    print(f"Found {len(video_files)} video file(s)")
    print("-" * 50)

    # Create output directory if specified
    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

    success_count = 0
    for video_file in sorted(video_files):
        if output_dir:
            output_file = out_path / f"{video_file.stem}.gif"
        else:
            output_file = None

        if convert_video_to_gif(str(video_file), str(output_file) if output_file else None, fps, width, quality):
            success_count += 1
        print()

    print("-" * 50)
    print(f"Processed {success_count}/{len(video_files)} files successfully")


def main():
    """Main function to parse arguments and convert videos to GIF."""

    if len(sys.argv) < 2:
        print("Usage: python video_to_gif.py <input_file_or_directory> [options]")
        print("\nOptions:")
        print("  --output <path>     Output file/directory path")
        print("  --fps <number>      Frames per second (default: 10)")
        print("                      Lower = smaller file, Less smooth")
        print("                      Higher = larger file, More smooth")
        print("                      Common values: 10, 15, 20, 24")
        print("  --width <pixels>    Width in pixels (height auto-calculated)")
        print("                      Common values: 320, 480, 640, 800")
        print("  --quality <level>   Quality: low, medium, high (default: medium)")
        print("                      low: 128 colors, smaller file")
        print("                      medium: 256 colors, balanced")
        print("                      high: 256 colors, best dithering")
        print("  --start <seconds>   Start time in seconds (for extracting segment)")
        print("  --duration <sec>    Duration in seconds (for extracting segment)")
        print("\nExamples:")
        print("  # Basic conversion")
        print("  python video_to_gif.py video.mp4")
        print()
        print("  # Custom size and quality")
        print("  python video_to_gif.py video.mp4 --width 480 --fps 15 --quality high")
        print()
        print("  # Extract segment (5 seconds starting at 10s)")
        print("  python video_to_gif.py video.mp4 --start 10 --duration 5")
        print()
        print("  # Process entire directory")
        print("  python video_to_gif.py videos/ --output gifs/ --width 640 --fps 20")
        print()
        print("  # Small file size")
        print("  python video_to_gif.py video.mp4 --width 320 --fps 10 --quality low")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = None
    fps = 10
    width = None
    quality = 'medium'
    start_time = None
    duration = None

    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--fps" and i + 1 < len(sys.argv):
            fps = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--width" and i + 1 < len(sys.argv):
            width = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--quality" and i + 1 < len(sys.argv):
            quality = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--start" and i + 1 < len(sys.argv):
            start_time = float(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--duration" and i + 1 < len(sys.argv):
            duration = float(sys.argv[i + 1])
            i += 2
        else:
            print(f"Unknown argument: {sys.argv[i]}")
            i += 1

    # Check if input is a file or directory
    input_path_obj = Path(input_path)
    if input_path_obj.is_file():
        # Process single file
        convert_video_to_gif(input_path, output_path, fps, width, quality, start_time, duration)
    elif input_path_obj.is_dir():
        # Process directory
        if start_time is not None or duration is not None:
            print("Warning: --start and --duration are ignored when processing directories")
        process_directory(input_path, output_path, fps, width, quality)
    else:
        print(f"Error: '{input_path}' is not a valid file or directory")


if __name__ == "__main__":
    main()
