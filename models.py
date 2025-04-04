from datetime import datetime
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    """User model for potential future authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    chats = db.relationship('Chat', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Chat(db.Model):
    """Model to store chat history."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    session_id = db.Column(db.String(128), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='chat', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Chat {self.id} Session: {self.session_id}>'

class Message(db.Model):
    """Model to store individual messages in a chat."""
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    is_user = db.Column(db.Boolean, default=True)  # True if message is from user, False if from bot
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message {self.id} User: {self.is_user}>'

class EmotionRecord(db.Model):
    """Model to store emotion analysis records."""
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    emotion = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmotionRecord {self.id} Emotion: {self.emotion}>'

class SongRecommendation(db.Model):
    """Model to store song recommendations."""
    id = db.Column(db.Integer, primary_key=True)
    emotion_record_id = db.Column(db.Integer, db.ForeignKey('emotion_record.id'), nullable=False)
    song_title = db.Column(db.String(128), nullable=False)
    artist = db.Column(db.String(128), nullable=False)
    url = db.Column(db.String(256), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SongRecommendation {self.id} Song: {self.song_title}>'