#!/usr/bin/env python3
"""
Script to extract audio from video files using ffmpeg.
"""

import os
import sys
import subprocess
from pathlib import Path


def extract_audio(video_path, output_path=None, audio_format='mp3', audio_quality='192k'):
    """
    Extract audio from a video file.

    Args:
        video_path: Path to the input video file
        output_path: Path for the output audio file (optional)
        audio_format: Output audio format (mp3, wav, aac, ogg, flac, m4a)
        audio_quality: Audio bitrate for compressed formats (e.g., '192k', '256k', '320k')

    Returns:
        bool: True if successful, False otherwise
    """
    video_path = Path(video_path)

    if not video_path.exists():
        print(f"✗ Error: Video file '{video_path}' does not exist.")
        return False

    # Determine output path
    if output_path is None:
        output_path = video_path.with_suffix(f'.{audio_format}')
    else:
        output_path = Path(output_path)

    print(f"Extracting audio from: {video_path.name}")
    print(f"Output: {output_path}")
    print(f"Format: {audio_format.upper()}, Quality: {audio_quality}")

    try:
        # Build ffmpeg command based on format
        if audio_format.lower() in ['mp3']:
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-vn',  # No video
                '-acodec', 'libmp3lame',
                '-b:a', audio_quality,
                '-y',  # Overwrite output file
                str(output_path)
            ]
        elif audio_format.lower() in ['wav']:
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-vn',
                '-acodec', 'pcm_s16le',  # PCM 16-bit
                '-ar', '44100',  # Sample rate
                '-ac', '2',  # Stereo
                '-y',
                str(output_path)
            ]
        elif audio_format.lower() in ['aac', 'm4a']:
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-vn',
                '-acodec', 'aac',
                '-b:a', audio_quality,
                '-y',
                str(output_path)
            ]
        elif audio_format.lower() in ['ogg']:
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-vn',
                '-acodec', 'libvorbis',
                '-b:a', audio_quality,
                '-y',
                str(output_path)
            ]
        elif audio_format.lower() in ['flac']:
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-vn',
                '-acodec', 'flac',
                '-y',
                str(output_path)
            ]
        else:
            print(f"✗ Error: Unsupported audio format '{audio_format}'")
            return False

        # Execute ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            file_size = output_path.stat().st_size / (1024 * 1024)  # Size in MB
            print(f"✓ Successfully extracted audio: {output_path.name} ({file_size:.2f} MB)")
            return True
        else:
            print(f"✗ Error extracting audio:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def process_directory(input_dir, output_dir=None, audio_format='mp3', audio_quality='192k'):
    """
    Extract audio from all video files in a directory.

    Args:
        input_dir: Directory containing video files
        output_dir: Output directory (if None, saves in same directory as video)
        audio_format: Output audio format
        audio_quality: Audio bitrate
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
            output_file = out_path / f"{video_file.stem}.{audio_format}"
        else:
            output_file = None

        if extract_audio(str(video_file), str(output_file) if output_file else None, audio_format, audio_quality):
            success_count += 1
        print()

    print("-" * 50)
    print(f"Processed {success_count}/{len(video_files)} files successfully")


def main():
    """Main function to parse arguments and extract audio."""

    if len(sys.argv) < 2:
        print("Usage: python extract_audio.py <input_file_or_directory> [options]")
        print("\nOptions:")
        print("  --output <path>     Output file/directory path")
        print("  --format <format>   Audio format: mp3, wav, aac, ogg, flac, m4a (default: mp3)")
        print("  --quality <bitrate> Audio bitrate for compressed formats (default: 192k)")
        print("                      Common values: 128k, 192k, 256k, 320k")
        print("\nExamples:")
        print("  python extract_audio.py video.mp4")
        print("  python extract_audio.py video.mp4 --format wav")
        print("  python extract_audio.py video.mp4 --output audio.mp3 --quality 320k")
        print("  python extract_audio.py videos/ --output audio/ --format mp3")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = None
    audio_format = 'mp3'
    audio_quality = '192k'

    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--format" and i + 1 < len(sys.argv):
            audio_format = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--quality" and i + 1 < len(sys.argv):
            audio_quality = sys.argv[i + 1]
            i += 2
        else:
            print(f"Unknown argument: {sys.argv[i]}")
            i += 1

    # Check if input is a file or directory
    input_path_obj = Path(input_path)
    if input_path_obj.is_file():
        # Process single file
        extract_audio(input_path, output_path, audio_format, audio_quality)
    elif input_path_obj.is_dir():
        # Process directory
        process_directory(input_path, output_path, audio_format, audio_quality)
    else:
        print(f"Error: '{input_path}' is not a valid file or directory")


if __name__ == "__main__":
    main()
