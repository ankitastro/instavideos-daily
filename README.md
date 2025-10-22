# InstaVideos Daily - Image and Video Processing Tools

A collection of Python scripts for processing images and videos for social media content creation.

## Features

- **Add Logo to Images**: Watermark images with a logo in any corner
- **Create Circular Images**: Convert astrologer photos to circular format with face detection
- **Create Circular Videos**: Convert videos to circular format with transparent backgrounds and face detection

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
- Customizable resolution
- Progress tracking during processing

## Requirements

Install dependencies:
```bash
pip install Pillow opencv-python
```

**System requirements:**
- Python 3.7+
- ffmpeg (must be installed and in PATH)

## Output Formats

- **Images**: PNG with alpha channel (transparency)
- **Videos**: MOV with PNG codec (transparency support)

## Face Detection

All circular conversion scripts use OpenCV's Haar Cascade face detection to:
1. Detect faces in the image/video
2. Center the crop around the detected face
3. Apply appropriate padding (2.5x face size)
4. Fall back to center crop if no face is detected

## License

This project is for personal/commercial use in social media content creation.
