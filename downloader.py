import os
import logging
from yt_dlp import YoutubeDL
from lyrics_fetcher import LyricsFetcher  # Import the LyricsFetcher class

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_music_and_lyrics(youtube_url, output_directory="downloads"):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'flac'},
        ],
        'outtmpl': os.path.join(output_directory, '%(title)s.%(ext)s'),
    }

    with YoutubeDL(ydl_opts) as ydl:
        logger.info(f"Downloading music from {youtube_url}")
        info = ydl.extract_info(youtube_url, download=True)
        title = info.get('title', 'Unknown Title')
        artist = info.get('uploader', 'Unknown Artist')
        logger.info(f"Downloaded: {title} by {artist}")

    song_id = info.get('id', None)
    saavn_has = False  # Set to True if lyrics are available on Saavn

    # Initialize LyricsFetcher and fetch lyrics
    lyrics_fetcher = LyricsFetcher()
    lyrics_data = lyrics_fetcher.get_lyrics(song_id, title, artist, saavn_has)

    # Save the lyrics to a file
    lyrics_file = os.path.join(output_directory, f"{title}.lrc")
    with open(lyrics_file, 'w', encoding='utf-8') as file:
        file.write(lyrics_data.get('lyrics', 'Lyrics not found.'))
    logger.info(f"Lyrics saved to: {lyrics_file}")

if __name__ == "__main__":
    youtube_link = input("Enter the YouTube URL: ")
    download_music_and_lyrics(youtube_link)
