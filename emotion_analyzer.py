import logging
import re
import random

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """
    A simple rule-based emotion analyzer for text.
    """
    
    def __init__(self):
        """Initialize the emotion analyzer with keyword patterns."""
        logger.info("Initializing simplified EmotionAnalyzer...")
        
        # Define emotion keyword patterns
        self.emotion_patterns = {
            'happy': [
                r'\b(happy|joy|joyful|glad|delighted|cheerful|content|pleased|thrilled|ecstatic)\b',
                r'\b(wonderful|amazing|excellent|fantastic|great|good|love|loving|enjoy|enjoyed)\b',
                r'😊|😄|😃|😀|🙂|😁|😍|🥰|❤️|💕'
            ],
            'sad': [
                r'\b(sad|unhappy|depressed|depressing|sorrow|sorry|grief|grieving|down|blue)\b',
                r'\b(upset|heartbroken|devastated|miserable|gloomy|troubled|regret|miss|missing)\b',
                r'😢|😥|😭|😔|😞|😟|💔|🥺|☹️|😿'
            ],
            'angry': [
                r'\b(angry|anger|mad|furious|annoyed|irritated|frustrated|rage|hate|hostile)\b',
                r'\b(outraged|bitter|resentful|disgusted|revolting|dislike|enraged|fuming)\b',
                r'😠|😡|🤬|💢|👿|😤|😒|👊|💥|🔥'
            ],
            'anxious': [
                r'\b(anxious|anxiety|worried|worry|nervous|stressed|stress|tense|afraid|scared)\b',
                r'\b(fear|frightened|panic|uneasy|concerned|dread|apprehensive|restless)\b',
                r'😰|😨|😧|😱|😖|😩|🤯|😬|😳|🥴'
            ],
            'excited': [
                r'\b(excited|exciting|thrilled|eager|enthusiastic|energetic|pumped|psyched)\b',
                r'\b(anticipation|looking forward|can\'t wait|thrilled|passionate|hyped)\b',
                r'🤩|🎉|🎊|✨|🙌|👏|⚡|🔥|💯|🚀'
            ],
            'neutral': [
                r'\b(ok|okay|fine|alright|so-so|meh|whatever|normal|average|moderate)\b',
                r'\b(indifferent|neither|balanced|impartial|standard|usual|common)\b'
            ],
            'annoyed': [
                r'\b(annoyed|annoying|irritated|irritating|bothered|bothering|frustrated)\b',
                r'\b(impatient|tired of|fed up|sick of|displeased|aggravated|irritable)\b',
                r'😒|😑|😐|🙄|😤|😫|🤦|🤨|😈|😏'
            ]
        }
    
    def analyze_emotion(self, text):
        """
        Analyze the emotion expressed in the given text using a simple rule-based approach.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            tuple: (emotion_name, confidence_score)
        """
        if not text or not text.strip():
            return "neutral", 1.0
        
        text = text.lower()
        
        # Count emotion pattern matches
        emotion_scores = {}
        for emotion, patterns in self.emotion_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text)
                score += len(matches)
            emotion_scores[emotion] = score
        
        # Find the emotion with the highest score
        max_score = max(emotion_scores.values()) if emotion_scores else 0
        
        # If no emotion patterns match, return neutral
        if max_score == 0:
            # Check for common greeting patterns
            if re.search(r'\b(hi|hello|hey|greetings|good morning|good afternoon|good evening)\b', text):
                return 'neutral', 0.9
            
            # Add some randomness to make it more interesting
            random_emotions = ['happy', 'neutral', 'excited']
            return random.choice(random_emotions), 0.6
        
        # Get all emotions with the max score (in case of ties)
        top_emotions = [emotion for emotion, score in emotion_scores.items() if score == max_score]
        
        # Calculate a confidence score between 0.7 and 0.95
        # Higher if there's only one top emotion and it has multiple matches
        confidence = min(0.7 + (0.05 * max_score), 0.95)
        if len(top_emotions) > 1:
            confidence = max(0.7, confidence - 0.1)  # Reduce confidence if there's a tie
        
        # Choose a random emotion from the top emotions (usually just one)
        chosen_emotion = random.choice(top_emotions)
        
        logger.debug(f"Detected emotion: {chosen_emotion} with confidence: {confidence}")
        return chosen_emotion, confidence
    
    def get_mood_description(self, mood):
        """
        Get a description of the given mood.
        
        Args:
            mood (str): The mood to describe
            
        Returns:
            str: A description of the mood
        """
        mood_descriptions = {
            'happy': [
                "You seem happy and in a positive mood!",
                "I'm picking up on your cheerful vibes!",
                "Your message radiates positivity and joy!"
            ],
            'sad': [
                "You're feeling down. Music can help lift your spirits.",
                "I sense some sadness in your message. Let's find something to cheer you up.",
                "It seems like you might be feeling a bit blue right now."
            ],
            'angry': [
                "You seem frustrated or angry right now.",
                "I detect some frustration in your words.",
                "Your message suggests you might be feeling upset or irritated."
            ],
            'anxious': [
                "I sense some anxiety or nervousness in your messages.",
                "You appear to be feeling worried or tense.",
                "Your message suggests you might be feeling a bit anxious."
            ],
            'excited': [
                "You're showing excitement and enthusiasm!",
                "I can feel your energy and excitement!",
                "Your message is full of anticipation and eagerness!"
            ],
            'neutral': [
                "Your mood seems balanced and neutral.",
                "I'm not detecting any strong emotions in your message.",
                "You seem to be in a fairly neutral state of mind."
            ],
            'annoyed': [
                "You appear to be annoyed or bothered by something.",
                "I detect a hint of irritation in your message.",
                "Your message suggests you might be feeling a bit impatient."
            ]
        }
        
        descriptions = mood_descriptions.get(mood, ["I'm not quite sure about your mood."])
        return random.choice(descriptions)