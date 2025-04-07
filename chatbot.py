import os
import json
import random
import re
import logging

logger = logging.getLogger(__name__)

class Chatbot:
    def __init__(self, intents_file="intents.json"):
        """
        Initialize the chatbot with a simplified pattern matching approach
        
        Args:
            intents_file: Path to the JSON file containing intents
        """
        logger.info("Initializing simplified Chatbot...")
        
        # Load the intents file
        try:
            with open(intents_file, 'r') as file:
                self.intents = json.load(file)
            logger.info(f"Successfully loaded intents from {intents_file}")
        except FileNotFoundError:
            logger.error(f"Intents file {intents_file} not found. Creating default intents.")
            self.intents = {
                "intents": [
                    {
                        "tag": "greeting",
                        "patterns": ["Hi", "Hello", "Hey", "How are you", "What's up"],
                        "responses": ["Hello! How are you feeling today?", "Hey there! How's your mood today?", "Hi! Ready to discover music that matches your mood?"]
                    },
                    {
                        "tag": "goodbye",
                        "patterns": ["Bye", "See you", "Goodbye", "I'm leaving", "Talk to you later"],
                        "responses": ["Goodbye! Come back when you want more music recommendations.", "See you later! Hope you enjoy the songs.", "Take care and enjoy the music!"]
                    },
                    {
                        "tag": "thanks",
                        "patterns": ["Thanks", "Thank you", "That's helpful", "Awesome, thanks", "Thanks for the help"],
                        "responses": ["Happy to help!", "Anytime!", "You're welcome.", "My pleasure."]
                    },
                    {
                        "tag": "music",
                        "patterns": ["Recommend songs", "What should I listen to", "Music recommendation", "Suggest some music", "Give me a playlist"],
                        "responses": ["I'll analyze your mood and recommend songs. How are you feeling?", "I need to understand your emotions to suggest the right music. Tell me more about how you feel.", "I'd be happy to recommend music based on your mood. Could you describe how you're feeling?"]
                    },
                    {
                        "tag": "mood_happy",
                        "patterns": ["I'm happy", "Feeling great", "I'm in a good mood", "Feeling joyful", "I'm excited"],
                        "responses": ["Glad to hear you're happy! I'll find some upbeat songs for you.", "Awesome! Let me recommend some positive music to match your mood.", "That's great! I'll suggest some cheerful tunes."]
                    },
                    {
                        "tag": "mood_sad",
                        "patterns": ["I'm sad", "Feeling down", "I'm depressed", "Not feeling good", "I'm upset"],
                        "responses": ["I'm sorry to hear that. Would you like some comforting music?", "I understand. I'll find some songs that might help you feel better.", "Let me recommend some music that might lift your spirits."]
                    },
                    {
                        "tag": "mood_angry",
                        "patterns": ["I'm angry", "I'm furious", "So annoyed", "I'm mad", "Feeling frustrated"],
                        "responses": ["I see you're feeling angry. Would you like some music to help release that tension?", "I'll suggest some tracks that might help you process those feelings.", "Let me find music that matches your intense energy right now."]
                    },
                    {
                        "tag": "mood_relaxed",
                        "patterns": ["I'm relaxed", "Feeling chill", "I'm calm", "Very peaceful", "I'm zen"],
                        "responses": ["Sounds like you're in a peaceful state. I'll find some music to maintain that vibe.", "Great! I'll recommend some gentle, calming tunes to match your mood.", "I have some perfect ambient tracks for your relaxed state."]
                    },
                    {
                        "tag": "help",
                        "patterns": ["Help", "What can you do", "How do you work", "What are your features", "How to use"],
                        "responses": ["I can analyze your emotions and recommend songs that match your mood. Just tell me how you're feeling or chat with me for a while.", "I'm an emotion-based music recommendation chatbot. I suggest songs based on how you're feeling. Just keep chatting and I'll analyze your mood.", "I recommend music based on your emotional state. The more you chat with me, the better I can understand your current mood."]
                    },
                    {
                        "tag": "hindi_music",
                        "patterns": ["Hindi songs", "Bollywood music", "Indian songs", "Recommend Hindi songs", "Suggest Bollywood songs"],
                        "responses": ["I'd be happy to recommend some Hindi songs! What mood are you in?", "Hindi songs are great! Let me find some based on your current mood.", "I can suggest Bollywood songs that match how you're feeling."]
                    },
                    {
                        "tag": "Your Name",
                        "patterns":["What is your name","Who are You","Tell me your name"],
                        "responses": ["My name Is ALEX2."]

                    },
                    {
                        "tag": "Who developed you",
                        "patterns":["Who developed you","Who created you","By whom you created"],
                        "responses": ["I was developed by Team of four individuls : Krishna Tripathi,Mohini Srivastava,Manuraj Singh,Manas Gupta"]
                    },
                    {
                        "tag": "What can you do",
                        "patterns":["What can you do","for what purpose were you created","what functions can you perform"],
                        "responses": ["I am a Song Recommender Bot, used to suggest songs depending upon the user's mood"]
                        
                ]
            }
            # Save the default intents to file
            with open(intents_file, 'w') as file:
                json.dump(self.intents, file, indent=4)
        
        # Extract patterns and create mappings
        self.intent_patterns = {}
        for intent in self.intents['intents']:
            self.intent_patterns[intent['tag']] = {
                'patterns': [pattern.lower() for pattern in intent['patterns']],
                'responses': intent['responses']
            }
            
        logger.info(f"Loaded {len(self.intent_patterns)} intents with patterns")
    
    def tokenize(self, sentence):
        """Simple tokenization by splitting on spaces and removing punctuation."""
        # Convert to lowercase and remove punctuation
        sentence = sentence.lower()
        # Replace punctuation with spaces
        sentence = re.sub(r'[^\w\s]', ' ', sentence)
        # Split on whitespace and remove empty tokens
        return [word for word in sentence.split() if word]
    
    def predict_class(self, sentence):
        """
        Find matching intents based on simple pattern matching.
        
        Args:
            sentence (str): User input
            
        Returns:
            list: Matched intents with confidence scores
        """
        if not sentence or not sentence.strip():
            return [{"intent": "greeting", "probability": "0.8"}]
        
        sentence = sentence.lower().strip()
        scores = {}
        
        # First check for exact matches
        for intent_tag, intent_data in self.intent_patterns.items():
            for pattern in intent_data['patterns']:
                if pattern in sentence:
                    scores[intent_tag] = scores.get(intent_tag, 0) + 1.0
        
        # If no exact matches, try word-level matching
        if not scores:
            tokens = self.tokenize(sentence)
            for intent_tag, intent_data in self.intent_patterns.items():
                for pattern in intent_data['patterns']:
                    pattern_tokens = self.tokenize(pattern)
                    
                    # Count how many words match
                    matches = sum(1 for token in tokens if token in pattern_tokens)
                    if matches > 0:
                        score = matches / max(len(tokens), len(pattern_tokens))
                        scores[intent_tag] = max(scores.get(intent_tag, 0), score)
        
        # Create a sorted list of intents and scores
        result = []
        for intent_tag, score in scores.items():
            result.append({"intent": intent_tag, "probability": str(score)})
        
        # Sort by probability (highest first)
        result.sort(key=lambda x: float(x["probability"]), reverse=True)
        
        # If no matches found, return greeting as default
        if not result:
            return [{"intent": "greeting", "probability": "0.7"}]
        
        return result
    
    def get_response(self, message):
        """
        Get a response based on the predicted intent.
        
        Args:
            message (str): User input
            
        Returns:
            str: Chatbot response
        """
        try:
            intents_list = self.predict_class(message)
            
            if not intents_list:
                # Fallback if no intent matched
                return "I'm not sure I understand. Could you rephrase that?"
            
            tag = intents_list[0]["intent"]
            responses = self.intent_patterns[tag].get('responses', None)
            
            if responses:
                return random.choice(responses)
            else:
                return "I'm still learning to understand different topics. Could you try asking something else?"
        except Exception as e:
            logger.error(f"Error getting response: {str(e)}")
            return "Sorry, I encountered an error. Please try again."
