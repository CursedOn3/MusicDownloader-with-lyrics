import json
import logging
import re
import requests
from typing import Dict, Optional

class LyricsFetcher:
    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_lyrics(self, track_id: str, title: str, artist: str, saavn_has: bool = False) -> Dict[str, str]:
        """
        Fetch lyrics from multiple sources
        
        Args:
            track_id (str): Track identifier
            title (str): Song title
            artist (str): Artist name
            saavn_has (bool): Whether Saavn lyrics are available
        
        Returns:
            Dict containing lyrics, type, and source
        """
        result = {
            'lyrics': '',
            'type': 'text',
            'source': '',
            'id': track_id
        }

        # Try Spotify lyrics first
        spotify_lyrics = self.get_spotify_lyrics(title, artist)
        if spotify_lyrics['lyrics']:
            return spotify_lyrics

        # If Spotify fails, try alternative sources
        if saavn_has:
            # Try Saavn lyrics
            self.logger.info('Getting Lyrics from Saavn')
            result['lyrics'] = self.get_saavn_lyrics(track_id)
            result['type'] = 'text'
            result['source'] = 'Jiosaavn'

            if not result['lyrics']:
                # Recursive fallback if Saavn fails
                return self.get_lyrics(track_id, title, artist, saavn_has=False)
        else:
            # Try Musixmatch
            self.logger.info('Trying Musixmatch lyrics')
            result['lyrics'] = self.get_musixmatch_lyrics(title, artist)
            result['type'] = 'text'
            result['source'] = 'Musixmatch'

            if not result['lyrics']:
                # Try Google if Musixmatch fails
                self.logger.info('Trying Google lyrics')
                result['lyrics'] = self.get_google_lyrics(title, artist)
                result['type'] = 'text'
                result['source'] = 'Google'

        return result

    def get_saavn_lyrics(self, lyrics_id: str) -> str:
        """
        Fetch lyrics from Jiosaavn
        
        Args:
            lyrics_id (str): Lyrics identifier
        
        Returns:
            str: Lyrics text
        """
        try:
            url = f'https://www.jiosaavn.com/api.php?__call=lyrics.getLyrics&lyrics_id={lyrics_id}&ctx=web6dot0&api_version=4&_format=json'
            headers = {'Accept': 'application/json'}
            response = requests.get(url, headers=headers)
            
            raw_lyrics = response.text.split('-->')
            lyrics_data = json.loads(raw_lyrics[-1])
            
            return lyrics_data['lyrics'].replace('<br>', '\n')
        except Exception as e:
            self.logger.error(f'Error fetching Saavn lyrics: {e}')
            return ''

    def get_spotify_lyrics(self, title: str, artist: str) -> Dict[str, str]:
        """
        Fetch lyrics from Spotify
        
        Args:
            title (str): Song title
            artist (str): Artist name
        
        Returns:
            Dict with lyrics, type, and source
        """
        # Note: This is a placeholder. Actual Spotify API access would require 
        # authentication and potentially different implementation
        result = {
            'lyrics': '',
            'type': 'text',
            'source': 'Spotify'
        }
        
        # Implement Spotify lyrics fetching logic here
        # This would typically involve:
        # 1. Authenticating with Spotify
        # 2. Searching for the track
        # 3. Retrieving lyrics
        
        return result

    def get_google_lyrics(self, title: str, artist: str) -> str:
        """
        Scrape lyrics from Google search
        
        Args:
            title (str): Song title
            artist (str): Artist name
        
        Returns:
            str: Lyrics text
        """
        base_url = 'https://www.google.com/search'
        delimiter1 = '</div></div></div></div><div class="hwc"><div class="BNeawe tAd8D AP7Wnd"><div><div class="BNeawe tAd8D AP7Wnd">'
        delimiter2 = '</div></div></div></div></div><div><span class="hwc"><div class="BNeawe uEec3 AP7Wnd">'
        
        search_queries = [
            f'{title} by {artist} lyrics',
            f'{title} by {artist} song lyrics',
            f'{title.split("-")[0]} by {artist} lyrics'
        ]
        
        for query in search_queries:
            try:
                params = {'q': query, 'client': 'safari'}
                response = requests.get(base_url, params=params)
                
                lyrics = response.text.split(delimiter1)[-1].split(delimiter2)[0]
                
                if '<meta charset="UTF-8">' not in lyrics:
                    return lyrics.strip()
            except Exception:
                continue
        
        return ''

    def get_musixmatch_lyrics(self, title: str, artist: str) -> str:
        """
        Fetch lyrics from Musixmatch
        
        Args:
            title (str): Song title
            artist (str): Artist name
        
        Returns:
            str: Lyrics text
        """
        try:
            # Find lyrics link
            link = self._get_musixmatch_link(title, artist)
            if not link:
                return ''
            
            # Scrape lyrics from the link
            return self._scrape_musixmatch_lyrics(link)
        except Exception as e:
            self.logger.error(f'Error fetching Musixmatch lyrics: {e}')
            return ''

    def _get_musixmatch_link(self, title: str, artist: str) -> Optional[str]:
        """
        Find Musixmatch lyrics link
        
        Args:
            title (str): Song title
            artist (str): Artist name
        
        Returns:
            Optional link to lyrics page
        """
        url = f'https://www.musixmatch.com/search/{title} {artist}'
        response = requests.get(url)
        
        if response.status_code != 200:
            return None
        
        match = re.search(r'href=\"(\/lyrics\/.*?)\"', response.text)
        return match.group(1) if match else None

    def _scrape_musixmatch_lyrics(self, path: str) -> str:
        """
        Scrape lyrics from Musixmatch
        
        Args:
            path (str): Path to lyrics page
        
        Returns:
            str: Lyrics text
        """
        url = f'https://www.musixmatch.com{path}'
        response = requests.get(url)
        
        if response.status_code != 200:
            return ''
        
        lyrics_matches = re.findall(
            r'<span class=\"lyrics__content__ok\">(.*?)<\/span>', 
            response.text, 
            re.DOTALL
        )
        
        return '\n'.join(lyrics_matches) if lyrics_matches else ''

# Example usage
if __name__ == '__main__':
    fetcher = LyricsFetcher()
    result = fetcher.get_lyrics('some_id', 'Song Title', 'Artist Name')
    print(result)