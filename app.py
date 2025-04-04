import os
import logging

from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "emotion-music-chatbot-secret")

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///chatbot.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
# initialize the app with the extension
db.init_app(app)

# Import after app initialization to avoid circular imports
from chatbot import Chatbot
from emotion_analyzer import EmotionAnalyzer
from music_recommender import MusicRecommender

# Initialize components
chatbot = Chatbot()
emotion_analyzer = EmotionAnalyzer()
music_recommender = MusicRecommender()

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()

@app.route('/')
def index():
    """Render the main chat interface."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Process chat messages and return response with emotion analysis and song recommendations."""
    try:
        user_message = request.json.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Store chat history in session
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        # Add user message to history
        session['chat_history'].append({'role': 'user', 'content': user_message})
        
        # Get chatbot response
        bot_response = chatbot.get_response(user_message)
        
        # Analyze emotion from recent messages
        recent_messages = " ".join([msg['content'] for msg in session['chat_history'][-5:] if msg['role'] == 'user'])
        emotion, confidence = emotion_analyzer.analyze_emotion(recent_messages)
        
        # Get song recommendations based on emotion
        songs = music_recommender.get_recommendations(emotion)
        
        # Create response object
        response = {
            'message': bot_response,
            'emotion': {
                'name': emotion,
                'confidence': confidence
            },
            'songs': songs
        }
        
        # Add bot response to history
        session['chat_history'].append({'role': 'bot', 'content': bot_response})
        
        # Keep session history to a reasonable size
        if len(session['chat_history']) > 20:
            session['chat_history'] = session['chat_history'][-20:]
        
        # Save session
        session.modified = True
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return jsonify({'error': 'An error occurred processing your message. Please try again.'}), 500

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    """Clear the chat history stored in the session."""
    if 'chat_history' in session:
        session.pop('chat_history')
    return jsonify({'status': 'success'})

@app.route('/search_hindi_songs', methods=['POST'])
def search_hindi_songs():
    """Search for Hindi songs based on user query."""
    try:
        query = request.json.get('query', '')
        
        if not query:
            return jsonify({'error': 'No search query provided'}), 400
            
        # Search for Hindi songs
        songs = music_recommender.search_hindi_songs(query)
        
        return jsonify({'songs': songs})
        
    except Exception as e:
        logger.error(f"Error searching for Hindi songs: {str(e)}")
        return jsonify({'error': 'An error occurred during search. Please try again.'}), 500
        
@app.route('/hindi_recommendations/<emotion>', methods=['GET'])
def hindi_recommendations(emotion):
    """Get Hindi song recommendations for a specific emotion."""
    try:
        if emotion not in music_recommender.hindi_music_tags:
            return jsonify({'error': 'Invalid emotion. Please use one of: happy, sad, angry, anxious, excited, neutral, annoyed'}), 400
            
        # Get Hindi recommendations for the emotion
        limit = request.args.get('limit', default=5, type=int)
        songs = music_recommender.get_hindi_recommendations(emotion, limit)
        
        return jsonify({'emotion': emotion, 'songs': songs})
        
    except Exception as e:
        logger.error(f"Error getting Hindi recommendations: {str(e)}")
        return jsonify({'error': 'An error occurred while getting recommendations. Please try again.'}), 500