# InstaVideos Daily - Image and Video Processing Tools

A comprehensive collection of Python scripts for processing images and videos for social media content creation, specifically designed for astrology and similar content.

## Features

- **Add Logo to Images**: Watermark images with a logo in any corner with customizable position and scale
- **Create Circular Images**: Convert photos to circular format with intelligent face detection and transparent backgrounds
- **Create Circular Videos**: Convert videos to circular format with transparent backgrounds, face detection, and smooth processing
- **Extract Audio**: Extract audio from video files in multiple formats (MP3, WAV, AAC, OGG, FLAC, M4A)

## Quick Start

All scripts support both single file and batch directory processing. Perfect for creating professional social media content at scale.

## Scripts

### 1. add_logo_to_images.py
Adds a logo watermark to images using ffmpeg.

**Usage:**
```bash
python add_logo_to_images.py <input_directory> [logo_path] [options]

Options:
  --position <pos>    Position: top-right, top-left, bottom-right, bottom-left (default: top-right)
  --margin <pixels>   Margin from edges in pixels (default: 10)
  --scale <ratio>     Logo scale relative to image width (default: 0.15)
  --output <dir>      Output directory (default: input_dir/with_logo)
```

**Example:**
```bash
python add_logo_to_images.py simple_ads/hasthrekha logo.png --position bottom-right --margin 20
```

### 2. make_circular.py
Converts images to circular format with face detection and transparent backgrounds.

**Usage:**
```bash
python make_circular.py <input_directory> [output_directory] [--size SIZE]

Options:
  --size SIZE    Output resolution in pixels (default: 500)
```

**Example:**
```bash
python make_circular.py AstroImages AstroImages_circular --size 500
```

**Features:**
- Face detection to ensure proper centering
- Transparent background (PNG output)
- Uniform resolution across all images
- Processes entire directory trees

### 3. make_video_circular.py
Converts videos to circular format with face detection and transparent backgrounds.

**Usage:**
```bash
python make_video_circular.py <input_directory> [output_directory] [--size SIZE]

Options:
  --size SIZE    Output resolution in pixels (default: 500)
```

**Example:**
```bash
# Process single video
python -c "
from make_video_circular import make_video_circular
make_video_circular('input.mp4', 'output.mov', 1000)
"

# Process directory
python make_video_circular.py circular_videos output --size 1000
```

**Features:**
- Face detection on first frame for optimal centering
- Transparent background (MOV output with PNG codec)
- Customizable resolution (typically 1000x1000 for social media)
- Progress tracking during processing
- Batch processing support

### 4. extract_audio.py
Extract audio from video files in various formats and quality levels.

**Usage:**
```bash
python extract_audio.py <input_file_or_directory> [options]

Options:
  --output <path>     Output file/directory path
  --format <format>   Audio format: mp3, wav, aac, ogg, flac, m4a (default: mp3)
  --quality <bitrate> Audio bitrate for compressed formats (default: 192k)
                      Common values: 128k, 192k, 256k, 320k
```

**Examples:**
```bash
# Extract audio from single video (default: MP3, 192k)
python extract_audio.py video.mp4

# Extract as high-quality WAV (lossless)
python extract_audio.py video.mp4 --format wav

# Extract with high quality MP3
python extract_audio.py video.mp4 --output audio.mp3 --quality 320k

# Process entire directory
python extract_audio.py videos/ --output audio/ --format mp3

# Extract as AAC
python extract_audio.py video.mp4 --format aac --quality 256k
```

**Features:**
- Support for multiple audio formats (MP3, WAV, AAC, OGG, FLAC, M4A)
- Customizable bitrate for compressed formats
- Batch directory processing
- Preserves audio quality with configurable settings
- Fast extraction using ffmpeg

## Typical Workflow

### For Circular Videos with Audio:
```bash
# 1. Create circular video from original
python -c "from make_video_circular import make_video_circular; make_video_circular('video.mp4', 'output.mov', 1000)"

# 2. Extract audio from original video
python extract_audio.py video.mp4 --quality 320k

# 3. Now you have both circular video (output.mov) and audio (video.mp3) ready for editing
```

### For Astrologer Profile Images:
```bash
# Convert all astrologer images to circular format
python make_circular.py AstroImages/ output/ --size 500

# Add watermark to promotional images
python add_logo_to_images.py simple_ads/ logo.png --position bottom-right --margin 20
```

## Requirements

Install dependencies:
```bash
pip install Pillow opencv-python
```

**System requirements:**
- Python 3.7+
- ffmpeg (must be installed and in PATH)

## Output Formats

- **Circular Images**: PNG with alpha channel (transparency)
- **Circular Videos**: MOV with PNG codec (full transparency support)
- **Audio**: MP3, WAV, AAC, OGG, FLAC, or M4A (configurable)
- **Watermarked Images**: Same format as input (preserves quality)

## Face Detection

All circular conversion scripts use OpenCV's Haar Cascade face detection to:
1. Detect faces in the image/video (first frame for videos)
2. Center the crop around the detected face
3. Apply appropriate padding (2.5x face size for optimal framing)
4. Fall back to center crop if no face is detected
5. Ensure proper head framing (forehead, hair, and face)

This ensures that your astrologer profile images and videos are always properly framed with faces centered.

## Technical Details

### Video Processing
- **Resolution**: Typically 1000x1000 pixels for Instagram/social media
- **Transparency**: Full alpha channel support via MOV container with PNG codec
- **Face Detection**: Processes first frame to determine optimal crop area
- **Performance**: Progress tracking shows frames processed in real-time

### Image Processing
- **Batch Processing**: Process entire directories of images at once
- **Uniform Output**: All images in a batch have the same resolution
- **Quality**: Uses LANCZOS resampling for high-quality scaling
- **Format**: PNG output preserves transparency

### Audio Extraction
- **Quality Presets**: 128k (low), 192k (standard), 256k (high), 320k (max)
- **Formats**: Lossy (MP3, AAC, OGG) and Lossless (WAV, FLAC)
- **Speed**: Fast extraction using ffmpeg's optimized codecs

## Use Cases

This toolkit is perfect for:
- **Astrology Content Creators**: Create circular profile videos with voiceovers
- **Social Media Marketing**: Add watermarks to promotional materials
- **Video Production**: Extract audio for editing, create circular overlays
- **Batch Processing**: Process hundreds of images/videos automatically
- **Professional Branding**: Maintain consistent circular format across all content

## License

This project is for personal/commercial use in social media content creation.
