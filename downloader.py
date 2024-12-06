import os
import json
import logging
import requests
from yt_dlp import YoutubeDL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Lyrics:
    @staticmethod
    def get_lyrics(id, title, artist, saavn_has):
        result = {
            'lyrics': '',
            'type': 'text',
            'source': '',
            'id': id,
        }

        logger.info('Getting Synced Lyrics')
        res = Lyrics.get_spotify_lyrics(title, artist)
        result['lyrics'] = res['lyrics']
        result['type'] = res['type']
        result['source'] = res['source']

        if not result['lyrics']:
            logger.info('Synced Lyrics not found. Getting text lyrics')
            if saavn_has:
                logger.info('Getting Lyrics from Saavn')
                result['lyrics'] = Lyrics.get_saavn_lyrics(id)
                result['type'] = 'text'
                result['source'] = 'Jiosaavn'

                if not result['lyrics']:
                    res = Lyrics.get_lyrics(id, title, artist, False)
                    result.update(res)
            else:
                logger.info('Lyrics not available on Saavn, finding on Musixmatch')
                result['lyrics'] = Lyrics.get_musixmatch_lyrics(title, artist)
                result['type'] = 'text'
                result['source'] = 'Musixmatch'

                if not result['lyrics']:
                    logger.info('Lyrics not found on Musixmatch, searching on Google')
                    result['lyrics'] = Lyrics.get_google_lyrics(title, artist)
                    result['type'] = 'text'
                    result['source'] = 'Google'

        return result

    @staticmethod
    def get_saavn_lyrics(song_id):
        try:
            url = f"https://www.jiosaavn.com/api.php?__call=lyrics.getLyrics&lyrics_id={song_id}&ctx=web6dot0&api_version=4&_format=json"
            headers = {'Accept': 'application/json'}
            response = requests.get(url, headers=headers)
            raw_lyrics = response.text.split('-->')
            fetched_lyrics = json.loads(raw_lyrics[1] if len(raw_lyrics) > 1 else raw_lyrics[0])
            lyrics = fetched_lyrics['lyrics'].replace('<br>', '\n')
            return lyrics
        except Exception as e:
            logger.error('Error in get_saavn_lyrics', exc_info=True)
            return ''

    @staticmethod
    def get_spotify_lyrics(title, artist):
        result = {
            'lyrics': '',
            'type': 'text',
            'source': 'Spotify',
        }
        try:
            # Spotify lyrics retrieval logic (mock example)
            logger.info(f"Fetching Spotify lyrics for {title} by {artist}")
            mock_response = {'tracks': {'items': [{'id': 'track_id', 'name': title, 'artists': [{'name': artist}]}]}}
            track = mock_response['tracks']['items'][0]
            if Lyrics.match_songs(title, artist, track['name'], track['artists'][0]['name']):
                result = Lyrics.get_spotify_lyrics_from_id(track['id'])
        except Exception as e:
            logger.error('Error in get_spotify_lyrics', exc_info=True)
        return result

    @staticmethod
    def get_spotify_lyrics_from_id(track_id):
        result = {
            'lyrics': '',
            'type': 'text',
            'source': 'Spotify',
        }
        try:
            url = f"https://spotify-lyric-api-984e7b4face0.herokuapp.com/?trackid={track_id}&format=lrc"
            headers = {'Accept': 'application/json'}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                lyrics_data = response.json()
                if not lyrics_data.get('error', True):
                    lines = lyrics_data.get('lines', [])
                    if lyrics_data.get('syncType') == 'LINE_SYNCED':
                        result['lyrics'] = '\n'.join(f"[{line['timeTag']}] {line['words']}" for line in lines)
                        result['type'] = 'lrc'
                    else:
                        result['lyrics'] = '\n'.join(line['words'] for line in lines)
            else:
                logger.error(f"get_spotify_lyrics_from_id returned {response.status_code}: {response.text}")
        except Exception as e:
            logger.error('Error in get_spotify_lyrics_from_id', exc_info=True)
        return result

    @staticmethod
    def get_google_lyrics(title, artist):
        try:
            base_url = "https://www.google.com/search?q="
            search_query = f"{title} by {artist} lyrics"
            response = requests.get(base_url + search_query)
            return "Mocked Google lyrics"  # Update with real scraping logic
        except Exception as e:
            logger.error('Error in get_google_lyrics', exc_info=True)
            return ''

    @staticmethod
    def get_musixmatch_lyrics(title, artist):
        try:
            link = Lyrics.get_lyrics_link(title, artist)
            logger.info(f'Found Musixmatch Lyrics Link: {link}')
            lyrics = Lyrics.scrap_link(link)
            return lyrics
        except Exception as e:
            logger.error('Error in get_musixmatch_lyrics', exc_info=True)
            return ''

    @staticmethod
    def get_lyrics_link(song, artist):
        try:
            url = f"https://www.musixmatch.com/search/{song} {artist}"
            response = requests.get(url)
            match = next(iter([m for m in response.text.split('href=') if '/lyrics/' in m]), None)
            return match.split('"')[0] if match else ''
        except Exception as e:
            logger.error('Error in get_lyrics_link', exc_info=True)
            return ''

    @staticmethod
    def scrap_link(unencoded_path):
        try:
            url = f"https://www.musixmatch.com{unencoded_path}"
            response = requests.get(url)
            return "Mocked Musixmatch lyrics"  # Update with real scraping logic
        except Exception as e:
            logger.error('Error in scrap_link', exc_info=True)
            return ''

    @staticmethod
    def match_songs(title, artist, title2, artist2):
        return title.lower() == title2.lower() and artist.lower() == artist2.lower()

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
    saavn_has = False
    lyrics_data = Lyrics.get_lyrics(song_id, title, artist, saavn_has)

    lyrics_file = os.path.join(output_directory, f"{title}.lrc")
    with open(lyrics_file, 'w', encoding='utf-8') as file:
        file.write(lyrics_data.get('lyrics', 'Lyrics not found.'))
    logger.info(f"Lyrics saved to: {lyrics_file}")

if __name__ == "__main__":
    youtube_link = input("Enter the YouTube URL: ")
    download_music_and_lyrics(youtube_link)
