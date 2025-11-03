# InstaVideos Daily - Image and Video Processing Tools

A comprehensive collection of Python scripts for processing images and videos for social media content creation, specifically designed for astrology and similar content.

## Sample Output

Here's an example of a circular video created with this toolkit:

![Circular Video Sample](samples/circular_video_sample.gif)

*Circular video with face detection and transparent background - perfect for social media overlays*

## Features

- **Add Logo to Images**: Watermark images with a logo in any corner with customizable position and scale
- **Create Circular Images**: Convert photos to circular format with intelligent face detection and transparent backgrounds
- **Create Circular Videos**: Convert videos to circular format with transparent backgrounds, face detection, and smooth processing
- **Extract Audio**: Extract audio from video files in multiple formats (MP3, WAV, AAC, OGG, FLAC, M4A)
- **Video to GIF**: Convert videos to high-quality GIF format with customizable size and quality

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
python make_video_circular.py <input_directory> [output_directory] [OPTIONS]

Options:
  --size SIZE         Output resolution in pixels (default: 500)
  --radius SCALE      Crop radius scale around face (default: 2.5)
                      Higher = wider radius (more context)
                      Lower = tighter crop (closer to face)
                      Typical range: 2.0 (tight) to 4.0 (wide)
```

**Examples:**
```bash
# Process single video
python -c "
from make_video_circular import make_video_circular
make_video_circular('input.mp4', 'output.mov', 1000, 3.5)
"

# Process directory with default settings
python make_video_circular.py circular_videos output --size 1000

# Process with wider radius for more context
python make_video_circular.py circular_videos output --size 1000 --radius 3.5

# Tight crop focusing on face
python make_video_circular.py circular_videos --radius 2.0
```

**Features:**
- Face detection on first frame for optimal centering
- Adjustable crop radius for controlling how much context is captured
- Transparent background (MOV output with PNG codec)
- Customizable resolution (typically 1000x1000 for social media)
- Multiprocessing support (uses all CPU cores for faster processing)
- Real-time progress bars with tqdm
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

### 5. video_to_gif.py
Convert videos to high-quality GIF format with optimized color palettes.

**Usage:**
```bash
python video_to_gif.py <input_file_or_directory> [options]

Options:
  --output <path>     Output file/directory path
  --fps <number>      Frames per second (default: 10)
                      Lower = smaller file, Less smooth
                      Higher = larger file, More smooth
                      Common values: 10, 15, 20, 24
  --width <pixels>    Width in pixels (height auto-calculated)
                      Common values: 320, 480, 640, 800
  --quality <level>   Quality: low, medium, high (default: medium)
                      low: 128 colors, smaller file
                      medium: 256 colors, balanced
                      high: 256 colors, best dithering
  --start <seconds>   Start time in seconds (for extracting segment)
  --duration <sec>    Duration in seconds (for extracting segment)
```

**Examples:**
```bash
# Basic conversion
python video_to_gif.py video.mp4

# Custom size and quality
python video_to_gif.py video.mp4 --width 480 --fps 15 --quality high

# Extract 5-second segment starting at 10s
python video_to_gif.py video.mp4 --start 10 --duration 5

# Process entire directory
python video_to_gif.py videos/ --output gifs/ --width 640 --fps 20

# Small file size for sharing
python video_to_gif.py video.mp4 --width 320 --fps 10 --quality low
```

**Features:**
- Two-pass conversion with optimized color palette generation
- High-quality Lanczos scaling
- Multiple quality presets (128-256 colors)
- Advanced dithering algorithms (Floyd-Steinberg, Bayer)
- Extract specific time segments
- Batch directory processing
- Looping GIFs for social media

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

You are free to use, modify, and distribute this software for personal or commercial use.
