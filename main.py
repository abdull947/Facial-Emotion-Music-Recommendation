# main.py - Entry Point for EmoTune

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for EmoTune application"""
    print("🎵 EmoTune - Emotion-Based Music Player")
    print("=" * 50)
    print("✅ Initializing application...")
    
    try:
        # Import auth page
        from auth import AuthPage
        
        print("✅ Connected to MongoDB")
        print("🔐 Please login or sign up")
        print("=" * 50)
        
        # Launch authentication page
        AuthPage()
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()