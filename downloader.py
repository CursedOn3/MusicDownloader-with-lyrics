import os
import logging
from yt_dlp import YoutubeDL
from lyrics_fetcher import LyricsFetcher  # Import the LyricsFetcher class
from mutagen.flac import FLAC  # Import the FLAC class from mutagen

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def embed_lyrics_in_metadata(audio_file, lyrics):
    """
    Embed lyrics into the FLAC file metadata.
    
    Args:
        audio_file (str): Path to the FLAC file
        lyrics (str): Lyrics to be embedded into the metadata
    """
    try:
        audio = FLAC(audio_file)
        audio['LYRICS'] = lyrics  # Add lyrics under the 'LYRICS' tag
        audio.save()
        logger.info(f"Lyrics embedded in {audio_file}")
    except Exception as e:
        logger.error(f"Error embedding lyrics in metadata: {e}")

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

    # Path to the downloaded FLAC file
    audio_file = os.path.join(output_directory, f"{title}.flac")

    # Embed the lyrics into the FLAC file's metadata
    if os.path.exists(audio_file):
        embed_lyrics_in_metadata(audio_file, lyrics_data.get('lyrics', 'Lyrics not found.'))
    else:
        logger.error(f"Audio file {audio_file} not found.")

if __name__ == "__main__":
    youtube_link = input("Enter the YouTube URL: ")
    download_music_and_lyrics(youtube_link)
