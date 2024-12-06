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
    Embed metadata into the FLAC file.

    Args:
        audio_file (str): Path to the FLAC file
        title (str): Title of the song
        artist (str): Artist of the song
        album (str): Album name
        genre (str): Genre of the song
        year (str): Release year
        lyrics (str): Lyrics to be embedded into the metadata
    """
    try:
        audio = FLAC(audio_file)
        
        # Set metadata fields
        audio['title'] = title
        audio['artist'] = artist
        audio['album'] = album
        audio['genre'] = genre
        audio['year'] = year
        audio['LYRICS'] = lyrics  # Add lyrics under the 'LYRICS' tag
        audio['USLT'] = lyrics  # Adding USLT (unsynchronized lyrics) tag for compatibility

        # Save the metadata changes to the FLAC file
        audio.save()
        logger.info(f"Metadata successfully embedded in {audio_file}")
    except Exception as e:
        logger.error(f"Error embedding metadata in FLAC: {e}")
        return False
    return True

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
        album = info.get('album', 'Unknown Album')  # Attempt to fetch album info
        genre = info.get('genre', 'Unknown Genre')  # Attempt to fetch genre info
        year = info.get('release_year', 'Unknown Year')  # Attempt to fetch release year
        logger.info(f"Downloaded: {title} by {artist} from {album}, Genre: {genre}, Year: {year}")

    song_id = info.get('id', None)
    saavn_has = False  # Set to True if lyrics are available on Saavn

    # Initialize LyricsFetcher and fetch lyrics
    lyrics_fetcher = LyricsFetcher()
    lyrics_data = lyrics_fetcher.get_lyrics(song_id, title, artist, saavn_has)

    # Path to the downloaded FLAC file
    audio_file = os.path.join(output_directory, f"{title}.flac")

    # Check if the FLAC file exists
    if not os.path.exists(audio_file):
        logger.error(f"Audio file {audio_file} not found.")
        return

    # Log the audio file path
    logger.info(f"Embedding metadata into: {audio_file}")

    # Embed the metadata (including lyrics) into the FLAC file
    success = embed_metadata_in_flac(audio_file, title, artist, album, genre, year, lyrics_data.get('lyrics', 'Lyrics not found.'))

    if not success:
        logger.error(f"Failed to embed metadata in {audio_file}")
    else:
        logger.info(f"Metadata embedded successfully in {audio_file}")

if __name__ == "__main__":
    youtube_link = input("Enter the YouTube URL: ")
    download_music_and_lyrics(youtube_link)
