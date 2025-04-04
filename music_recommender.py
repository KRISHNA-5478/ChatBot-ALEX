import os
import requests
import logging
import random
from collections import defaultdict

logger = logging.getLogger(__name__)

class MusicRecommender:
    """
    Class for recommending music based on detected emotions using Last.fm API.
    """
    
    def __init__(self):
        """Initialize the music recommender with API keys and emotion-to-tag mappings."""
        logger.info("Initializing MusicRecommender...")
        
        # Get Last.fm API key from environment or use a default for testing
        self.api_key = os.getenv("LASTFM_API_KEY", "dd9e76929ad08db64ef2ecf588dc824d")  # Default is an example key
        self.api_base_url = "http://ws.audioscrobbler.com/2.0/"
        
        # Map emotions to music tags on Last.fm
        self.emotion_to_tags = {
            'happy': ['happy', 'upbeat', 'uplifting', 'feel good', 'cheerful', 'joyful'],
            'sad': ['sad', 'melancholy', 'emotional', 'heartbreak', 'ballad', 'slow'],
            'angry': ['angry', 'aggressive', 'intense', 'heavy', 'rage', 'metal'],
            'anxious': ['chill', 'ambient', 'relaxing', 'calm', 'meditation', 'peaceful'],
            'excited': ['energetic', 'dance', 'upbeat', 'party', 'exciting', 'uptempo'],
            'neutral': ['indie', 'alternative', 'pop', 'contemporary', 'moderate', 'pleasant'],
            'annoyed': ['soothing', 'mellow', 'soft', 'acoustic', 'gentle', 'calm']
        }
        
        # Fallback recommendations for when API calls fail
        self.fallback_recommendations = {
            'happy': [
                {'name': 'Happy', 'artist': 'Pharrell Williams', 'url': 'https://www.last.fm/music/Pharrell+Williams/_/Happy'},
                {'name': 'Uptown Funk', 'artist': 'Mark Ronson ft. Bruno Mars', 'url': 'https://www.last.fm/music/Mark+Ronson/_/Uptown+Funk'},
                {'name': 'Walking on Sunshine', 'artist': 'Katrina & The Waves', 'url': 'https://www.last.fm/music/Katrina+&+The+Waves/_/Walking+on+Sunshine'}
            ],
            'sad': [
                {'name': 'Someone Like You', 'artist': 'Adele', 'url': 'https://www.last.fm/music/Adele/_/Someone+Like+You'},
                {'name': 'Fix You', 'artist': 'Coldplay', 'url': 'https://www.last.fm/music/Coldplay/_/Fix+You'},
                {'name': 'Hurt', 'artist': 'Johnny Cash', 'url': 'https://www.last.fm/music/Johnny+Cash/_/Hurt'}
            ],
            'angry': [
                {'name': 'Break Stuff', 'artist': 'Limp Bizkit', 'url': 'https://www.last.fm/music/Limp+Bizkit/_/Break+Stuff'},
                {'name': 'Bulls on Parade', 'artist': 'Rage Against the Machine', 'url': 'https://www.last.fm/music/Rage+Against+the+Machine/_/Bulls+on+Parade'},
                {'name': 'Master of Puppets', 'artist': 'Metallica', 'url': 'https://www.last.fm/music/Metallica/_/Master+of+Puppets'}
            ],
            'anxious': [
                {'name': 'Weightless', 'artist': 'Marconi Union', 'url': 'https://www.last.fm/music/Marconi+Union/_/Weightless'},
                {'name': 'Clair de Lune', 'artist': 'Claude Debussy', 'url': 'https://www.last.fm/music/Claude+Debussy/_/Clair+de+Lune'},
                {'name': 'Gymnopédie No. 1', 'artist': 'Erik Satie', 'url': 'https://www.last.fm/music/Erik+Satie/_/Gymnop%C3%A9die+No.+1'}
            ],
            'excited': [
                {'name': "Can't Stop the Feeling!", 'artist': 'Justin Timberlake', 'url': 'https://www.last.fm/music/Justin+Timberlake/_/Can%27t+Stop+the+Feeling%21'},
                {'name': 'Dance Monkey', 'artist': 'Tones and I', 'url': 'https://www.last.fm/music/Tones+and+I/_/Dance+Monkey'},
                {'name': 'Dynamite', 'artist': 'BTS', 'url': 'https://www.last.fm/music/BTS/_/Dynamite'}
            ],
            'neutral': [
                {'name': 'Viva La Vida', 'artist': 'Coldplay', 'url': 'https://www.last.fm/music/Coldplay/_/Viva+La+Vida'},
                {'name': 'Clocks', 'artist': 'Coldplay', 'url': 'https://www.last.fm/music/Coldplay/_/Clocks'},
                {'name': 'Believer', 'artist': 'Imagine Dragons', 'url': 'https://www.last.fm/music/Imagine+Dragons/_/Believer'}
            ],
            'annoyed': [
                {'name': 'Pure Shores', 'artist': 'All Saints', 'url': 'https://www.last.fm/music/All+Saints/_/Pure+Shores'},
                {'name': 'Chilled Ibiza', 'artist': 'Cafe Del Mar', 'url': 'https://www.last.fm/music/Cafe+Del+Mar'},
                {'name': 'Porcelain', 'artist': 'Moby', 'url': 'https://www.last.fm/music/Moby/_/Porcelain'}
            ]
        }
        
        # Cache for storing recommendations to avoid repeated API calls
        self.recommendation_cache = defaultdict(list)
        
    def get_recommendations(self, emotion, limit=5):
        """
        Get music recommendations based on the detected emotion.
        
        Args:
            emotion (str): The detected emotion
            limit (int): Maximum number of recommendations to return
            
        Returns:
            list: A list of recommended songs with artist, title, and URL
        """
        # Check if we already have recommendations cached for this emotion
        if emotion in self.recommendation_cache and self.recommendation_cache[emotion]:
            logger.debug(f"Using cached recommendations for {emotion}")
            return self.recommendation_cache[emotion][:limit]
        
        # Get appropriate tags for the emotion
        tags = self.emotion_to_tags.get(emotion, self.emotion_to_tags['neutral'])
        
        # Choose a random tag from the list for variety
        tag = random.choice(tags)
        
        try:
            # Make API request to Last.fm
            params = {
                'method': 'tag.gettoptracks',
                'tag': tag,
                'api_key': self.api_key,
                'format': 'json',
                'limit': 20  # Get more results to have a good selection
            }
            
            response = requests.get(self.api_base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'tracks' in data and 'track' in data['tracks']:
                    tracks = data['tracks']['track']
                    
                    # Filter and format results
                    recommendations = []
                    for track in tracks:
                        if len(recommendations) >= limit:
                            break
                            
                        # Create recommendation object
                        recommendation = {
                            'name': track.get('name', 'Unknown Track'),
                            'artist': track.get('artist', {}).get('name', 'Unknown Artist'),
                            'url': track.get('url', '#')
                        }
                        
                        recommendations.append(recommendation)
                    
                    # Cache the recommendations
                    self.recommendation_cache[emotion] = recommendations
                    
                    return recommendations
                else:
                    logger.warning(f"No tracks found for tag {tag}")
            else:
                logger.error(f"Last.fm API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error getting music recommendations: {str(e)}")
        
        # Return fallback recommendations if API call fails
        logger.info(f"Using fallback recommendations for {emotion}")
        return self.fallback_recommendations.get(emotion, self.fallback_recommendations['neutral'])[:limit]
    
    def get_recommendation_by_artist(self, artist_name, limit=3):
        """
        Get recommendations for a specific artist.
        
        Args:
            artist_name (str): The name of the artist
            limit (int): Maximum number of recommendations to return
            
        Returns:
            list: A list of recommended songs by the artist
        """
        try:
            # Make API request to Last.fm
            params = {
                'method': 'artist.gettoptracks',
                'artist': artist_name,
                'api_key': self.api_key,
                'format': 'json',
                'limit': limit
            }
            
            response = requests.get(self.api_base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'toptracks' in data and 'track' in data['toptracks']:
                    tracks = data['toptracks']['track']
                    
                    # Format results
                    recommendations = []
                    for track in tracks:
                        recommendation = {
                            'name': track.get('name', 'Unknown Track'),
                            'artist': artist_name,
                            'url': track.get('url', '#')
                        }
                        
                        recommendations.append(recommendation)
                    
                    return recommendations
                else:
                    logger.warning(f"No tracks found for artist {artist_name}")
            else:
                logger.error(f"Last.fm API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error getting artist recommendations: {str(e)}")
        
        # Return empty list if API call fails
        return []
