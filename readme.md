# YouTube Subtitle Downloader

An interactive command-line tool that downloads subtitles from YouTube videos or entire channels and can merge them into a single searchable document.

## Features

- Download subtitles from single videos or entire YouTube channels
- Support for multiple languages (English, Spanish, French, and many more)
- Multiple subtitle formats (SRT, VTT, ASS, LRC)
- Option to include auto-generated subtitles
- Merge all subtitles from a channel into a single text file for easy searching
- User-friendly interactive menu system
- Real-time progress tracking
- Customizable output directory

## Requirements

- Python 3.6 or higher
- yt-dlp (installed automatically if missing)
- FFmpeg (optional, required for subtitle format conversion)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install yt-dlp
```

3. For subtitle format conversion, install FFmpeg:

**Windows:**
- Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
- Extract the downloaded ZIP file
- Add the bin folder to your system PATH or place ffmpeg.exe in the same directory as this script

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

## Usage

1. Run the script:

```bash
python youtube_subtitle_downloader.py
```

2. Follow the interactive prompts:
   - Enter a YouTube video or channel URL
   - Select whether it's a channel or single video
   - Choose the subtitle language
   - Select the subtitle format
   - Choose whether to include auto-generated subtitles
   - For channels, choose whether to merge subtitles into a single file
   - Select an output directory or use the default

## Example Usage

### Downloading Subtitles from a YouTube Channel

1. Start the script and select "Download YouTube Subtitles"
2. Enter the channel URL (e.g., https://www.youtube.com/c/ChannelName)
3. Select "Channel" when asked about URL type
4. Choose your preferred language (e.g., English)
5. Select a subtitle format (SRT recommended for best compatibility)
6. Choose whether to include auto-generated subtitles
7. Select "Yes" to merge all subtitles into a single text file
8. Choose an output directory or use the default
9. Confirm and start the download

### Downloading Subtitles from a Single Video

1. Start the script and select "Download YouTube Subtitles"
2. Enter the video URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID)
3. Select "Single video" when asked about URL type
4. Choose your preferred language
5. Select a subtitle format
6. Choose whether to include auto-generated subtitles
7. Choose an output directory or use the default
8. Confirm and start the download

## Output Files

- Individual subtitle files are saved in the specified output directory
- For channels, subtitle files are organized by video
- When merging is enabled, a single text file containing all subtitles is created
- The merged file includes headers to identify which subtitles belong to which video

## Troubleshooting

### FFmpeg Not Found

If you see an error like:
```
ERROR: Preprocessing: ffmpeg not found. Please install or provide the path using --ffmpeg-location
```

You need to install FFmpeg as described in the Installation section. Without FFmpeg, the script will still download subtitles but won't be able to convert between formats.

### No Subtitles Found

Not all YouTube videos have subtitles available. The script will:
- Try to download manual subtitles first
- Fall back to auto-generated subtitles if available and enabled
- Report if no subtitles were found

### Subtitle Format Issues

If you encounter issues with a specific subtitle format:
- Try SRT format, which has the best compatibility
- Enable auto-generated subtitles, which are more widely available
- Check if the video actually has subtitles in your selected language

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Uses [yt-dlp](https://github.com/yt-dlp/yt-dlp), a powerful YouTube downloader
- Inspired by the need for accessible YouTube content analysis
