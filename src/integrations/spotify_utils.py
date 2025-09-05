# ============================================================================
# src/integrations/spotify_utils.py - Spotify Integration Module
# ============================================================================
import os
import logging
from typing import List, Dict, Optional
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpotifyMoodRecommender:
    """Spotify integration for mood-based playlist recommendations."""
    
    def __init__(self):
        """Initialize Spotify client with credentials from environment variables."""
        self.client = None
        self._initialize_client()
        
        # Mood to search terms mapping
        self.mood_keywords = {
            'happy': ['happy', 'upbeat', 'positive', 'cheerful', 'joyful'],
            'sad': ['sad', 'melancholy', 'emotional', 'heartbreak', 'blue'],
            'angry': ['angry', 'rage', 'metal', 'punk', 'aggressive'],
            'surprised': ['energetic', 'exciting', 'surprise', 'uplifting', 'dynamic'],
            'fear': ['calm', 'relaxing', 'soothing', 'peaceful', 'meditation'],
            'disgust': ['alternative', 'indie', 'experimental', 'unique', 'different'],
            'neutral': ['chill', 'ambient', 'focus', 'study', 'background'],
            'energetic': ['workout', 'pump up', 'energetic', 'motivation', 'power'],
            'relaxed': ['chill', 'lounge', 'ambient', 'relaxing', 'calm'],
            'romantic': ['love', 'romantic', 'valentine', 'date night', 'intimate']
        }
    
    def _initialize_client(self) -> None:
        """Initialize Spotify client with error handling."""
        try:
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                logger.error("Spotify credentials not found in environment variables")
                logger.error("Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file")
                return
            
            # Set up client credentials flow
            client_credentials_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            
            self.client = spotipy.Spotify(
                client_credentials_manager=client_credentials_manager,
                requests_timeout=10
            )
            
            # Test connection
            self.client.search(q='test', limit=1)
            logger.info("Spotify client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Spotify client: {str(e)}")
            self.client = None
    
    def _get_search_terms(self, mood: str) -> List[str]:
        """Get search terms for a given mood."""
        mood_lower = mood.lower().strip()
        return self.mood_keywords.get(mood_lower, ['music', 'playlist', 'songs'])
    
    def _search_playlists(self, search_term: str, limit: int = 10) -> List[Dict]:
        """Search for playlists using a specific term."""
        try:
            results = self.client.search(
                q=search_term,
                type='playlist',
                limit=limit,
                market='US'
            )
            
            playlists = []
            for playlist in results['playlists']['items']:
                if playlist and playlist.get('name') and playlist.get('external_urls'):
                    playlist_data = {
                        'name': playlist['name'],
                        'url': playlist['external_urls']['spotify'],
                        'image': None,
                        'description': playlist.get('description', ''),
                        'total_tracks': playlist.get('tracks', {}).get('total', 0),
                        'owner': playlist.get('owner', {}).get('display_name', 'Unknown')
                    }
                    
                    # Get image URL
                    if playlist.get('images') and len(playlist['images']) > 0:
                        playlist_data['image'] = playlist['images'][0]['url']
                    
                    playlists.append(playlist_data)
            
            return playlists
            
        except Exception as e:
            logger.error(f"Error searching playlists for '{search_term}': {str(e)}")
            return []
    
    def get_playlists_by_mood(self, mood: str, n_playlists: int = 5) -> List[Dict]:
        """
        Get playlist recommendations based on mood.
        
        Args:
            mood (str): The detected emotion/mood
            n_playlists (int): Number of playlists to return
            
        Returns:
            List[Dict]: List of playlist dictionaries with name, url, image, etc.
        """
        if not self.client:
            logger.warning("Spotify client not available. Returning empty list.")
            return []
        
        if not mood:
            logger.warning("No mood provided. Using 'music' as default search term.")
            mood = 'music'
        
        try:
            search_terms = self._get_search_terms(mood)
            all_playlists = []
            
            # Search using different terms to get variety
            for term in search_terms[:3]:  # Use first 3 terms to avoid too many API calls
                playlists = self._search_playlists(f"{term} playlist", limit=10)
                all_playlists.extend(playlists)
                
                if len(all_playlists) >= n_playlists * 2:  # Get extra to filter duplicates
                    break
            
            # Remove duplicates and filter by quality
            seen_names = set()
            unique_playlists = []
            
            for playlist in all_playlists:
                name_lower = playlist['name'].lower()
                if (name_lower not in seen_names and 
                    len(playlist['name']) > 3 and  # Filter out very short names
                    playlist['total_tracks'] > 10):  # Filter out small playlists
                    
                    seen_names.add(name_lower)
                    unique_playlists.append(playlist)
                    
                    if len(unique_playlists) >= n_playlists:
                        break
            
            logger.info(f"Found {len(unique_playlists)} playlists for mood: {mood}")
            return unique_playlists[:n_playlists]
            
        except Exception as e:
            logger.error(f"Error getting playlists for mood '{mood}': {str(e)}")
            return []
    
    def is_available(self) -> bool:
        """Check if Spotify client is available and working."""
        return self.client is not None


# Global instance for easy importing
_spotify_recommender = None

def get_spotify_recommender() -> SpotifyMoodRecommender:
    """Get the global Spotify recommender instance."""
    global _spotify_recommender
    if _spotify_recommender is None:
        _spotify_recommender = SpotifyMoodRecommender()
    return _spotify_recommender

def get_playlists_by_mood(mood: str, n_playlists: int = 5) -> List[Dict]:
    """
    Convenience function to get playlists by mood.
    
    Args:
        mood (str): The detected emotion/mood
        n_playlists (int): Number of playlists to return
        
    Returns:
        List[Dict]: List of playlist dictionaries
    """
    recommender = get_spotify_recommender()
    return recommender.get_playlists_by_mood(mood, n_playlists)

def is_spotify_available() -> bool:
    """Check if Spotify integration is available."""
    recommender = get_spotify_recommender()
    return recommender.is_available()