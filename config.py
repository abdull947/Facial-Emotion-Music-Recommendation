import os
import warnings

# ==================== SUPPRESS WARNINGS ====================
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  

from pymongo import MongoClient

# ==================== MONGODB CONFIGURATION ====================
MONGO_URI = "mongodb://localhost:27017/"  
DB_NAME = "emotune_db"

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  

# Initialize MongoDB connection
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Collections
    users_collection = db['users']
    favorites_collection = db['favorites']
    history_collection = db['history']
    cache_collection = db['songs_cache']
    
    # NEW: Collections for new features
    settings_collection = db['user_settings']  # User preferences
    statistics_collection = db['user_statistics']  # Usage stats
    
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    db = None

# ==================== FOLDERS ====================
CACHE_FOLDER = "music_cache"
FACES_FOLDER = "captured_faces"
PROFILE_PICS_FOLDER = "profile_pictures"  # NEW: Profile pictures

# Create folders
for folder in [CACHE_FOLDER, FACES_FOLDER, PROFILE_PICS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# ==================== COLORS ====================
COLORS = {
    'primary': '#E74C3C',
    'primary_dark': '#C0392B',
    'dark_bg': '#0f0f0f',
    'card_bg': '#1e1e1e',
    'text': '#ffffff',
    'text_secondary': '#b3b3b3',
    'success': '#2ECC71',
    'warning': '#FFD700',
    'emotions': {
        'happy': '#FF6B6B',
        'sad': '#4ECDC4',
        'angry': '#FF4757',
        'fear': '#A29BFE',
        'disgust': '#6C5CE7',
        'surprise': '#FD79A8',
        'neutral': '#95A5A6'
    }
}

# NEW: Light theme colors
COLORS_LIGHT = {
    'primary': '#E74C3C',
    'primary_dark': '#C0392B',
    'dark_bg': '#f5f5f5',
    'card_bg': '#ffffff',
    'text': '#000000',
    'text_secondary': '#666666',
    'success': '#2ECC71',
    'warning': '#FFD700',
    'emotions': {
        'happy': '#FF6B6B',
        'sad': '#4ECDC4',
        'angry': '#FF4757',
        'fear': '#A29BFE',
        'disgust': '#6C5CE7',
        'surprise': '#FD79A8',
        'neutral': '#95A5A6'
    }
}

# ==================== SETTINGS ====================
# Emotion Detection
CAPTURE_HOLD_TIME = 1.5
CONFIDENCE_THRESHOLD = 0.5
MIN_FACE_SIZE = 130

# Music Search
SONGS_PER_EMOTION = 7
SONG_MIN_DURATION = 180  # 3 minutes
SONG_MAX_DURATION = 900  # 15 minutes

# NEW: Default user settings
DEFAULT_SETTINGS = {
    'theme': 'dark',  # 'dark' or 'light'
    'notifications': True,
    'email_updates': False,
    'auto_play': True,
    'save_history': True,
    'language': 'en'  # 'en' or 'ur'
}

# ==================== LOAD FER MODEL ====================
print("🚀 Loading emotion detection model...")
from fer.fer import FER
DETECTOR = FER(mtcnn=True)
print("✅ Model loaded!")