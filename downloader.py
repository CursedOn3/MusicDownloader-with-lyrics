import os
import logging
from yt_dlp import YoutubeDL
from lyrics_fetcher import LyricsFetcher  # Import the LyricsFetcher class
from mutagen.flac import FLAC  # Import the FLAC class from mutagen

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def embed_metadata_in_flac(audio_file, title, artist, album, genre, year, lyrics):
    """
    Embed metadata into the FLAC file with more robust handling.
    """
    try:
        audio = FLAC(audio_file)
        
        # Explicitly set metadata, avoiding 'Unknown' values
        metadata_fields = {
            'title': title if title and title != 'Unknown Title' else None,
            'artist': artist if artist and artist != 'Unknown Artist' else None,
            'album': album if album and album != 'Unknown Album' else None,
            'genre': genre if genre and genre != 'Unknown Genre' else None,
            'date': year if year and year != 'Unknown Year' else None,
        }

        for key, value in metadata_fields.items():
            if value:
                audio[key] = str(value)

        # Add lyrics with more robust handling
        if lyrics and lyrics != 'Lyrics not found.':
            audio['LYRICS'] = lyrics
            audio['USLT'] = lyrics

        audio.save()
        logger.info(f"Metadata successfully embedded in {audio_file}")
        return True
    except Exception as e:
        logger.error(f"Error embedding metadata in FLAC: {e}")
        return False

def download_music_and_lyrics(youtube_url, output_directory="downloads"):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'flac'},
        ],
        'outtmpl': os.path.join(output_directory, '%(title)s.%(ext)s'),
        'extract_flat': True,  # Add this to get more metadata
    }

    with YoutubeDL(ydl_opts) as ydl:
        logger.info(f"Downloading music from {youtube_url}")
        info = ydl.extract_info(youtube_url, download=True)
        
        # Enhanced metadata extraction
        title = info.get('title') or input("Enter song title: ")
        artist = info.get('uploader') or input("Enter artist name: ")
        album = info.get('album') or input("Enter album name: ")
        genre = info.get('genre') or input("Enter genre: ")
        year = info.get('release_year') or input("Enter release year: ")

        logger.info(f"Metadata: {title} by {artist} from {album}")


if __name__ == "__main__":
    youtube_link = input("Enter the YouTube URL: ")
    download_music_and_lyrics(youtube_link)
