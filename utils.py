# utils.py
import random
from datetime import datetime
from config import *
import os

# ==================== USER MANAGEMENT ====================
def get_current_user():
    """Get currently logged in user"""
    if os.path.exists('.current_user'):
        with open('.current_user', 'r') as f:
            return f.read().strip()
    return None

def set_current_user(username):
    """Set current user"""
    with open('.current_user', 'w') as f:
        f.write(username)

def logout_user():
    """Logout current user"""
    if os.path.exists('.current_user'):
        os.remove('.current_user')

def user_exists(username):
    """Check if user exists"""
    return users_collection.find_one({'username': username}) is not None

def create_user(username, password_hash):
    """Create new user"""
    user_data = {
        'username': username,
        'password': password_hash,
        'created_at': datetime.now()
    }
    users_collection.insert_one(user_data)

def verify_user(username, password_hash):
    """Verify user credentials"""
    user = users_collection.find_one({'username': username})
    if user and user.get('password') == password_hash:
        return True
    return False

# ==================== CACHE ====================
def load_cache_index():
    """Load cache from MongoDB"""
    cache_doc = cache_collection.find_one({'_id': 'music_cache'})
    if cache_doc:
        return cache_doc.get('data', {})
    return {}

def save_cache_index(cache):
    """Save cache to MongoDB"""
    cache_collection.update_one(
        {'_id': 'music_cache'},
        {'$set': {'data': cache}},
        upsert=True
    )

def get_cache_path(video_id):
    return os.path.join(CACHE_FOLDER, f"{video_id}.mp3")

# ==================== FAVORITES ====================
def load_favorites(username=None):
    """Load favorites for specific user from MongoDB"""
    if username is None:
        username = get_current_user()
    
    if not username:
        return {}
    
    fav_doc = favorites_collection.find_one({'username': username})
    if fav_doc:
        return fav_doc.get('favorites', {})
    return {}

def save_favorites(user_favorites, username=None):
    """Save favorites for specific user to MongoDB"""
    if username is None:
        username = get_current_user()
    
    if not username:
        return
    
    favorites_collection.update_one(
        {'username': username},
        {'$set': {'favorites': user_favorites, 'updated_at': datetime.now()}},
        upsert=True
    )

# ==================== HISTORY ====================
def load_history(username=None):
    """Load history for specific user from MongoDB"""
    if username is None:
        username = get_current_user()
    
    if not username:
        return []
    
    # Get all history entries for this user, sorted by timestamp descending
    history_entries = list(history_collection.find(
        {'user': username}
    ).sort('timestamp', -1).limit(50))
    
    # Convert MongoDB documents to dicts and remove _id
    for entry in history_entries:
        entry.pop('_id', None)
    
    return history_entries

def add_to_history(emotion, confidence, face_image_path, songs):
    """Add session to user's history in MongoDB"""
    username = get_current_user()
    if not username:
        return
    
    entry = {
        'timestamp': datetime.now(),
        'emotion': emotion,
        'confidence': confidence,
        'face_image': face_image_path,
        'songs': songs,
        'user': username,
        'date_formatted': datetime.now().strftime("%B %d, %Y at %I:%M %p")
    }
    
    history_collection.insert_one(entry)
    
    # Keep only last 50 entries per user
    user_history = list(history_collection.find(
        {'user': username}
    ).sort('timestamp', -1))
    
    if len(user_history) > 50:
        # Delete oldest entries
        entries_to_delete = user_history[50:]
        ids_to_delete = [entry['_id'] for entry in entries_to_delete]
        history_collection.delete_many({'_id': {'$in': ids_to_delete}})

def clear_history(username=None):
    """Clear history for specific user from MongoDB"""
    if username is None:
        username = get_current_user()
    
    if not username:
        return
    
    history_collection.delete_many({'user': username})

# ==================== PAKISTANI MUSIC SEARCH ====================

def get_dynamic_query(emotion):
    """Generate Pakistani music queries for each emotion"""
    
    # Pakistani artists and genres per emotion
    pakistani_music = {
        "happy": {
            "artists": ["Atif Aslam", "Rahat Fateh Ali Khan", "Ali Zafar", "Abrar ul Haq", "Hadiqa Kiani"],
            "genres": ["Pakistani pop", "Punjabi songs", "Pakistani wedding songs"],
            "moods": ["happy", "upbeat", "romantic", "celebration", "joyful"]
        },
        "sad": {
            "artists": ["Rahat Fateh Ali Khan", "Atif Aslam", "Bilal Khan", "Shafqat Amanat Ali", "Strings"],
            "genres": ["Pakistani sad songs", "ghazal", "emotional songs", "heartbreak songs"],
            "moods": ["sad", "emotional", "heartbreak", "melancholic", "dard bhare", "painful"]
        },
        "angry": {
            "artists": ["Young Stunners", "Talha Anjum", "Bohemia", "Faris Shafi"],
            "genres": ["Pakistani rap", "desi hip hop", "Pakistani rock", "underground rap"],
            "moods": ["angry", "aggressive", "intense", "powerful", "rebel", "fierce"]
        },
        "fear": {
            "artists": ["Nusrat Fateh Ali Khan", "Abida Parveen", "Junoon"],
            "genres": ["qawwali", "sufi music", "Pakistani classical", "spiritual music"],
            "moods": ["dark", "mysterious", "intense", "spiritual", "deep", "haunting"]
        },
        "disgust": {
            "artists": ["Noori", "Sajid & Zeeshan", "Junoon", "Entity Paradigm"],
            "genres": ["Pakistani rock", "hard rock", "alternative rock", "metal"],
            "moods": ["heavy", "intense", "aggressive", "powerful", "strong", "bold"]
        },
        "surprise": {
            "artists": ["Asim Azhar", "Abdullah Siddiqui", "Hasan Raheem", "Talal Qureshi"],
            "genres": ["Pakistani electronic", "desi EDM", "fusion music", "experimental"],
            "moods": ["energetic", "surprising", "modern", "upbeat", "fresh", "dynamic"]
        },
        "neutral": {
            "artists": ["Strings", "Jal", "Call", "Aaroh", "Fuzon"],
            "genres": ["Pakistani soft rock", "chill songs", "lofi desi", "acoustic"],
            "moods": ["chill", "relaxing", "calm", "peaceful", "mellow", "soft"]
        }
    }
    
    # Get emotion data
    emotion_data = pakistani_music.get(emotion, pakistani_music["neutral"])
    
    # Random selections
    artist = random.choice(emotion_data["artists"])
    genre = random.choice(emotion_data["genres"])
    mood = random.choice(emotion_data["moods"])
    
    # Query patterns specifically for Pakistani music
    patterns = [
        f"{artist} {mood} songs",
        f"{genre} {mood}",
        f"Pakistani {mood} songs",
        f"{artist} best songs",
        f"{genre} playlist",
        f"Pakistani songs {mood}",
        f"{mood} {genre}",
        f"{artist} latest songs",
        f"Urdu {mood} songs",
        f"Pakistani {genre}",
        f"{mood} Urdu songs",
        f"best Pakistani {mood} songs",
        f"{artist} hit songs",
        f"{genre} collection",
        f"Pakistani music {mood}"
    ]
    
    query = random.choice(patterns)
    
    # Add Pakistani/Urdu/Hindi modifiers 70% of the time
    if random.random() > 0.3:
        modifiers = ["Pakistani", "Urdu", "desi", "Pak", "Pakistan"]
        if random.choice(modifiers) not in query:
            query = f"{random.choice(modifiers)} {query}"
    
    # Add year/trending 40% of the time
    if random.random() > 0.6:
        time_mods = ["2024", "2025", "new", "latest", "trending", "popular", "best", "top hits"]
        query = f"{query} {random.choice(time_mods)}"
    
    return query.strip()

def parse_duration(duration_str):
    """Parse duration string to seconds"""
    if not duration_str or ':' not in duration_str:
        return 0
    try:
        parts = duration_str.split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0
    except:
        return 0

def search_youtube_music(emotion, ytmusic):
    """Search YouTube Music for Pakistani songs with dynamic queries"""
    try:
        # Use dynamic Pakistani query
        query = get_dynamic_query(emotion)
        print(f"🇵🇰 Searching: '{query}'")
        
        results = ytmusic.search(query, filter='songs', limit=20)
        
        songs = []
        for result in results:
            if result.get('resultType') == 'song':
                video_id = result.get('videoId')
                title = result.get('title', 'Unknown')
                artists = result.get('artists', [])
                artist = artists[0]['name'] if artists else 'Unknown'
                duration_str = result.get('duration', '0:00')
                duration = parse_duration(duration_str)
                
                if SONG_MIN_DURATION <= duration <= SONG_MAX_DURATION:
                    songs.append({
                        'id': video_id,
                        'title': title,
                        'artist': artist,
                        'duration': duration,
                        'duration_str': duration_str
                    })
                    
                    if len(songs) >= SONGS_PER_EMOTION:
                        break
        
        return songs
    except Exception as e:
        print(f"❌ Search error: {e}")
        return []

def get_cached_or_search(emotion, ytmusic):
    
    # Load cache from MongoDB
    cache_doc = cache_collection.find_one({'_id': 'music_cache'})

    if cache_doc:
        cache_data = cache_doc.get('data', {})
        
        # Check if we have this emotion cached
        if emotion in cache_data:
            cached_songs = cache_data[emotion].get('songs', [])
            
            # Verify that downloaded audio files still exist
            valid_songs = []
            for song in cached_songs:
                audio_path = get_cache_path(song['id'])
                if os.path.exists(audio_path):
                    valid_songs.append(song)
            
            # If we have at least 3 valid cached songs, use them
            if len(valid_songs) >= 3:
                print(f"✅ Found {len(valid_songs)} cached songs for {emotion.upper()}!")
                print(f"🎵 Playing from cache (no download needed)")
                
                # Update last used timestamp in MongoDB
                cache_data[emotion]['last_used'] = datetime.now()
                cache_collection.update_one(
                    {'_id': 'music_cache'},
                    {'$set': {f'data.{emotion}.last_used': datetime.now()}},
                    upsert=True
                )
                
                return valid_songs
    
    # No cached songs or not enough - fetch new ones
    print(f"🎵 Finding fresh Pakistani songs for {emotion.upper()}...")
    
    # Use dynamic Pakistani query
    query = get_dynamic_query(emotion)
    print(f"🇵🇰 Searching: '{query}'")
    
    songs = search_youtube_music(emotion, ytmusic)
    
    if songs:
        print(f"✅ Found {len(songs)} Pakistani songs!")
        
        # Save to MongoDB cache
        cache_entry = {
            'songs': songs,
            'last_fetched': datetime.now(),
            'last_used': datetime.now(),
            'query': query
        }
        
        cache_collection.update_one(
            {'_id': 'music_cache'},
            {'$set': {f'data.{emotion}': cache_entry}},
            upsert=True
        )
        
        return songs
    else:
        print("❌ No songs found")
        return []
    
def clear_old_cache_mongodb(days=30):
    """
    Clean up old cached songs from MongoDB that haven't been used in X days
    Also delete corresponding audio files
    """
    cache_doc = cache_collection.find_one({'_id': 'music_cache'})
    
    if not cache_doc:
        return
    
    cache_data = cache_doc.get('data', {})
    current_time = datetime.now()
    
    emotions_to_remove = []
    files_deleted = 0
    
    for emotion, data in cache_data.items():
        last_used = data.get('last_used')
        
        # Handle both datetime objects and None
        if last_used is None:
            last_used = data.get('last_fetched', current_time)
        
        # Calculate days difference
        if isinstance(last_used, datetime):
            days_diff = (current_time - last_used).days
        else:
            days_diff = 0
        
        # If not used in X days, mark for removal
        if days_diff > days:
            emotions_to_remove.append(emotion)
            
            # Delete audio files
            for song in data.get('songs', []):
                audio_path = get_cache_path(song['id'])
                if os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                        files_deleted += 1
                        print(f"🗑️ Deleted: {song['title'][:40]}")
                    except Exception as e:
                        print(f"❌ Could not delete: {e}")
    
    # Remove from MongoDB
    if emotions_to_remove:
        update_data = {}
        for emotion in emotions_to_remove:
            update_data[f'data.{emotion}'] = ""
        
        cache_collection.update_one(
            {'_id': 'music_cache'},
            {'$unset': update_data}
        )
        
        print(f"🗑️ Cleaned {len(emotions_to_remove)} emotion caches ({files_deleted} files)")
    else:
        print("✅ No old cache to clean")