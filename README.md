# YouTube Music Downloader 🎵

## Overview

This Python script allows you to download music from YouTube, extract audio in FLAC format, and automatically fetch and embed metadata and lyrics.

## Features ✨

- Download music from YouTube URLs
- Convert to high-quality FLAC audio
- Automatic metadata extraction
- Lyrics fetching from multiple sources:
  - Spotify
  - Musixmatch
  - Google
  - Jiosaavn
- Metadata embedding in FLAC files

## Prerequisites 🛠

- Python 3.8+
- FFmpeg installed
- Required Python packages:
  - `yt-dlp`
  - `mutagen`
  - `requests`

## Installation 📦

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-music-downloader.git
cd youtube-music-downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage 🚀

### Command Line
```bash
python downloader.py
```

When prompted, enter a YouTube URL for the music you want to download.

### Programmatic Usage
```python
from downloader import download_music_and_lyrics

youtube_link = "https://youtube.com/your-music-video"
download_music_and_lyrics(youtube_link)
```

## How It Works 🔍

1. Downloads audio from YouTube
2. Converts to FLAC format
3. Attempts to fetch lyrics from multiple sources
4. Embeds metadata and lyrics into the FLAC file

## Troubleshooting 🐛

- Ensure FFmpeg is installed
- Check your internet connection
- Verify YouTube URL is valid
- Some songs might have limited metadata or lyric availability

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License 📄

[MIT License]

## Disclaimer ⚠️

Respect copyright laws. Use this tool only for personal use or with proper permissions.
