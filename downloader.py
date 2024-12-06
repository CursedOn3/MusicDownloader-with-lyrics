import os
import requests
from mutagen.flac import FLAC
from mutagen.id3 import ID3, USLT, Encoding
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Lyrics:
    @staticmethod
    def get_spotify_lyrics(title, artist):
        """
        Fetches Spotify lyrics based on title and artist.
        """
        result = {'lyrics': '', 'type': 'text', 'source': 'Spotify'}
        try:
            logger.info(f"Fetching Spotify lyrics for {title} by {artist}")
            spotify_api_url = "https://api.spotify.com/v1/search"
            headers = {"Authorization": "Bearer YOUR_SPOTIFY_ACCESS_TOKEN"}
            params = {"q": f"{title} {artist}", "type": "track", "limit": 1}
            response = requests.get(spotify_api_url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                items = data.get("tracks", {}).get("items", [])
                if items:
                    track_id = items[0].get("id")
                    lyrics_res = Lyrics.get_spotify_lyrics_from_id(track_id)
                    result.update(lyrics_res)
            else:
                logger.error(f"Spotify API error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error fetching Spotify lyrics: {e}", exc_info=True)
        return result

    @staticmethod
    def get_spotify_lyrics_from_id(track_id):
        """
        Fetches Spotify lyrics using the track ID.
        """
        result = {'lyrics': '', 'type': 'text', 'source': 'Spotify'}
        try:
            api_url = f"https://spotify-lyric-api-984e7b4face0.herokuapp.com/?trackid={track_id}&format=lrc"
            response = requests.get(api_url)

            if response.status_code == 200:
                data = response.json()
                if not data.get("error"):
                    lines = data.get("lines", [])
                    if data.get("syncType") == "LINE_SYNCED":
                        result['lyrics'] = "\n".join(
                            [f"[{line['timeTag']}] {line['words']}" for line in lines]
                        )
                        result['type'] = 'lrc'
                    else:
                        result['lyrics'] = "\n".join(line['words'] for line in lines)
                        result['type'] = 'text'
            else:
                logger.error(f"Spotify Lyrics API error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error fetching Spotify lyrics by ID: {e}", exc_info=True)
        return result

    @staticmethod
    def get_saavn_lyrics(song_id):
        """
        Fetches lyrics from JioSaavn using the song ID.
        """
        try:
            api_url = f"https://www.jiosaavn.com/api.php?__call=lyrics.getLyrics&lyrics_id={song_id}&ctx=web6dot0&api_version=4&_format=json"
            response = requests.get(api_url)

            if response.status_code == 200:
                data = response.json()
                lyrics = data.get("lyrics", "").replace("<br>", "\n")
                return lyrics
            else:
                logger.error(f"Saavn Lyrics API error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error fetching Saavn lyrics: {e}", exc_info=True)
        return ""

    @staticmethod
    def get_musixmatch_lyrics(title, artist):
        """
        Scrapes lyrics from Musixmatch.
        """
        try:
            search_url = f"https://www.musixmatch.com/search/{title} {artist}"
            response = requests.get(search_url)

            if response.status_code == 200:
                logger.info("Successfully fetched lyrics from Musixmatch (mock).")
                return "Mocked Musixmatch lyrics for the song."
            else:
                logger.error(f"Musixmatch error: {response.status_code}")
        except Exception as e:
            logger.error("Error fetching Musixmatch lyrics", exc_info=True)
        return ""

    @staticmethod
    def get_google_lyrics(title, artist):
        """
        Fetches lyrics by scraping Google search results.
        """
        try:
            search_query = f"{title} {artist} lyrics"
            search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            response = requests.get(search_url)

            if response.status_code == 200:
                logger.info("Successfully fetched lyrics from Google (mock).")
                return "Mocked Google lyrics for the song."
            else:
                logger.error(f"Google search error: {response.status_code}")
        except Exception as e:
            logger.error("Error fetching Google lyrics", exc_info=True)
        return ""

def embed_lyrics_in_metadata(audio_file, lyrics, source):
    """
    Embeds the fetched lyrics into the audio file's metadata.
    """
    try:
        if audio_file.endswith('.flac'):
            audio = FLAC(audio_file)
            audio['lyrics'] = lyrics
            audio.save()
            logger.info(f"Lyrics embedded into FLAC file: {audio_file}")
        elif audio_file.endswith('.mp3'):
            audio = ID3(audio_file)
            audio.add(USLT(encoding=Encoding.UTF8, lang="eng", desc=source, text=lyrics))
            audio.save()
            logger.info(f"Lyrics embedded into MP3 file: {audio_file}")
        else:
            logger.warning(f"Unsupported file format for embedding lyrics: {audio_file}")
    except Exception as e:
        logger.error(f"Error embedding lyrics into metadata: {e}", exc_info=True)

def main():
    audio_file = "path_to_audio_file.flac"  # Replace with the path to your audio file
    title = "Song Title"  # Replace with the title of the song
    artist = "Artist Name"  # Replace with the artist's name

    # Attempt to fetch lyrics from various sources
    lyrics_result = Lyrics.get_spotify_lyrics(title, artist)
    if not lyrics_result['lyrics']:
        lyrics_result['lyrics'] = Lyrics.get_saavn_lyrics("song_id") or \
                                  Lyrics.get_musixmatch_lyrics(title, artist) or \
                                  Lyrics.get_google_lyrics(title, artist)

    # Embed lyrics into audio file metadata
    if lyrics_result['lyrics']:
        embed_lyrics_in_metadata(audio_file, lyrics_result['lyrics'], lyrics_result['source'])
    else:
        logger.warning("No lyrics found to embed.")

if __name__ == "__main__":
    main()
