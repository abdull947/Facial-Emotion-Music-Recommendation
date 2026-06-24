# 🎵 EmoTune — Emotion-Based Music Player

EmoTune aapki face dekh ke emotion detect karta hai aur us ke hisaab se Pakistani music play karta hai!

---

## 🚀 Features

- 😊 **Emotion Detection** — Camera se face scan karke 7 emotions detect karta hai (happy, sad, angry, fear, disgust, surprise, neutral)
- 🎵 **Pakistani Music** — Emotion ke hisaab se YouTube Music se Pakistani/Urdu songs dhundhta hai
- ❤️ **Favorites** — Pasand ke gaane save karo
- 📜 **History** — Pichli sessions dekho
- 📊 **Statistics** — Aapki emotion history aur music stats
- ⚙️ **Settings** — Dark/Light theme, language, aur preferences
- 👤 **Admin Panel** — Users aur system manage karo
- 🔐 **Auth System** — Login / Signup with MongoDB

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| GUI | Tkinter |
| Emotion Detection | FER (Face Emotion Recognition) + MTCNN |
| Face Detection | OpenCV |
| Music Search | YouTube Music API (ytmusicapi) |
| Music Download | yt-dlp |
| Music Playback | Pygame |
| Database | MongoDB (pymongo) |
| Image Processing | Pillow, imageio |

---

## 📁 Project Structure

```
EmoTune/
├── main.py              # Entry point — yahan se start karo
├── auth.py              # Login / Signup page
├── config.py            # MongoDB, colors, settings config
├── utils.py             # Helper functions — user, cache, history, music search
├── ui_components.py     # Reusable UI components
├── admin_panel.py       # Admin dashboard
├── settings_page.py     # User settings page
├── statistics_page.py   # Usage statistics page
├── requirements.txt     # Required packages
├── .env.example         # Environment variables template
├── music_cache/         # Downloaded MP3 files (auto created)
├── captured_faces/      # Face images (auto created)
└── profile_pictures/    # User profile pics (auto created)
```

---

## ⚙️ Installation & Setup

### Step 1: MongoDB Install karo
MongoDB Community Edition download karo aur install karo:
👉 https://www.mongodb.com/try/download/community

### Step 2: Python Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 3: Packages Install karo
```bash
pip install -r requirements.txt
```

### Step 4: Environment Setup
```bash
# .env.example ko copy karo
copy .env.example .env   # Windows
cp .env.example .env     # Mac/Linux
```

### Step 5: Run karo!
```bash
python main.py
```

---

## 🎭 Supported Emotions

| Emotion | Pakistani Music Style |
|---------|----------------------|
| 😊 Happy | Atif Aslam, Ali Zafar — upbeat songs |
| 😢 Sad | Rahat Fateh Ali Khan, Strings — emotional ghazals |
| 😠 Angry | Young Stunners, Bohemia — desi rap |
| 😨 Fear | Nusrat Fateh Ali Khan — sufi qawwali |
| 🤢 Disgust | Junoon, Noori — rock music |
| 😲 Surprise | Asim Azhar, Hasan Raheem — modern fusion |
| 😐 Neutral | Strings, Jal — soft chill songs |

---

## ⚠️ Common Issues

**Camera nahi chal rahi?**
```bash
pip install opencv-python
```

**MongoDB connect nahi ho raha?**
- MongoDB service start karo: `net start MongoDB` (Windows)
- Ya MongoDB Compass use karo

**FER model slow hai?**
- Pehli baar model download hoga — thoda wait karo
- MTCNN ke liye internet chahiye

---

## 👨‍💻 Developer Notes

- `config.py` mein `MONGO_URI` change karo agar remote MongoDB use karni ho
- `SONGS_PER_EMOTION = 7` change karo zyada songs ke liye
- Cache automatically 30 din baad clear hoti hai
