# music_player.py
import tkinter as tk
import pygame
import threading
import time
import webbrowser
import urllib.parse
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageEnhance
import io
import requests
import yt_dlp
from utils import *
from config import *
import os

class MusicPlayer:
    def __init__(self, emotion, songs, parent_callback=None):
        self.root = tk.Tk()
        self.root.title("EmoTune Player")
        
        # CRITICAL: Hide window immediately to prevent flicker
        self.root.withdraw()
        
        self.root.state('zoomed')
        self.root.configure(bg='black')
        
        self.parent_callback = parent_callback
        self.emotion = emotion
        self.songs = songs
        self.current = 0
        self.is_paused = False
        self.is_playing = False
        self.song_duration = 0
        self.downloading = False
        self.seeking = False
        self.current_audio_path = None
        self.play_start_time = 0
        self.pause_time = 0
        self.is_running = True
        self.update_id = None
        
        current_user = get_current_user()
        user_favorites = load_favorites(current_user)
        self.is_liked = self.emotion in user_favorites
        
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        
        self.root.update_idletasks()
        
        self.create_ui()
        threading.Thread(target=self.play, daemon=True).start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # CRITICAL: Show window only after everything is ready
        self.root.deiconify()
        
        self.root.mainloop()

    def create_ui(self):
        # Canvas for background
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='black')
        self.canvas.pack(fill="both", expand=True)
        
        self.canvas.update()
        
        # Load background
        self.bg_image = self.load_background()
        
        # SMALLER Top bar (height 50)
        top_bar = tk.Frame(self.canvas, bg='#1a0f0a', height=50)
        top_bar_win = self.canvas.create_window(
            self.canvas.winfo_width() // 2, 25,
            window=top_bar, width=self.canvas.winfo_width(), height=50
        )
        
        tk.Button(top_bar, text="←", font=("Arial", 18, "bold"),
                 fg="white", bg='#1a0f0a', bd=0,
                 cursor="hand2", activebackground='#2a1510',
                 command=self.go_back).pack(side="left", padx=12)
        
        emotion_color = COLORS['emotions'].get(self.emotion.lower(), COLORS['primary'])
        tk.Label(top_bar, text=f"🎵 {self.emotion.upper()} MOOD", 
                font=("Arial", 16, "bold"),
                fg=emotion_color, bg='#1a0f0a').pack(side="left", expand=True)
        
        tk.Button(top_bar, text="", font=("Arial", 20, "bold"),
                 fg="white", bg='#1a0f0a', bd=0,
                 cursor="hand2").pack(side="right", padx=12)
        
        # COMPACT player container (fits screen better)
        player_container = tk.Frame(self.canvas, bg='#2a1f1a', width=550, height=620)
        player_window = self.canvas.create_window(
            self.canvas.winfo_width() // 2,
            self.canvas.winfo_height() // 2 + 25,
            window=player_container,
            anchor='center'
        )
        player_container.pack_propagate(False)
        
        # Update positions on resize
        def update_positions(event=None):
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            
            self.canvas.coords(top_bar_win, w // 2, 25)
            self.canvas.itemconfig(top_bar_win, width=w)
            
            self.canvas.coords(player_window, w // 2, h // 2 + 25)
        
        self.root.bind('<Configure>', update_positions)
        
        # Inner content
        inner = tk.Frame(player_container, bg='#2a1f1a')
        inner.pack(expand=True, pady=10)
        
        # SMALLER Album art (220x220 instead of 260x260)
        art_container = tk.Frame(inner, bg='#1a0f0a', 
                                width=220, height=220, bd=2, relief="solid")
        art_container.pack(pady=(5, 12))
        art_container.pack_propagate(False)
        
        self.art = tk.Label(art_container, bg='#0a0a0a')
        self.art.pack(fill="both", expand=True, padx=2, pady=2)
        self.set_default_art()
        
        # Song info (compact)
        self.song_label = tk.Label(inner, text="Loading...", 
                                   font=("Arial", 15, "bold"),
                                   fg="white", bg='#2a1f1a', 
                                   wraplength=500, justify="center")
        self.song_label.pack(pady=(6, 2))
        
        self.artist_label = tk.Label(inner, text="", 
                                     font=("Arial", 11),
                                     fg='#aaa', bg='#2a1f1a')
        self.artist_label.pack(pady=2)
        
        # Progress bar (compact)
        progress_bg = tk.Frame(inner, bg='#1a0f0a')
        progress_bg.pack(pady=10)
        
        progress_content = tk.Frame(progress_bg, bg='#1a0f0a')
        progress_content.pack(padx=18, pady=8)
        
        # Time labels and slider
        time_frame = tk.Frame(progress_content, bg='#1a0f0a')
        time_frame.pack(fill="x")
        
        self.time_start = tk.Label(time_frame, text="0:00", 
                                   font=("Arial", 9, "bold"), 
                                   fg='#aaa', bg='#1a0f0a')
        self.time_start.pack(side="left", padx=(0, 8))
        
        self.progress_var = tk.DoubleVar()
        self.progress_slider = tk.Scale(
            time_frame, from_=0, to=100, 
            orient="horizontal", variable=self.progress_var,
            showvalue=False, bg='#1a0f0a', fg=COLORS['primary'],
            troughcolor='#0a0a0a', activebackground=COLORS['primary'],
            highlightthickness=0, bd=0, sliderlength=13, length=420,
            command=self.on_slider_move
        )
        self.progress_slider.pack(side="left")
        
        self.progress_slider.bind("<ButtonPress-1>", self.on_seek_start)
        self.progress_slider.bind("<ButtonRelease-1>", self.on_seek_end)
        
        self.time_end = tk.Label(time_frame, text="0:00", 
                                font=("Arial", 9, "bold"), 
                                fg='#aaa', bg='#1a0f0a')
        self.time_end.pack(side="left", padx=(8, 0))
        
        # Control buttons (compact)
        controls = tk.Frame(inner, bg='#2a1f1a')
        controls.pack(pady=12)
        
        btn_style = {
            "font": ("Arial", 15), "bg": '#1a0f0a', "fg": "white",
            "bd": 0, "cursor": "hand2", "activebackground": "#0a0a0a",
            "width": 3, "height": 1
        }
        
        tk.Button(controls, text="🔀", **btn_style).grid(row=0, column=0, padx=5)
        tk.Button(controls, text="⏮", command=self.previous, 
                 **btn_style).grid(row=0, column=1, padx=5)
        
        self.play_pause_btn = tk.Button(
            controls, text="▶", command=self.play_pause,
            font=("Arial", 26, "bold"), bg=COLORS['primary'], fg="white",
            width=3, height=1, bd=0, cursor="hand2", 
            activebackground=COLORS['primary_dark']
        )
        self.play_pause_btn.grid(row=0, column=2, padx=8)
        
        tk.Button(controls, text="⏭", command=self.next, 
                 **btn_style).grid(row=0, column=3, padx=5)
        tk.Button(controls, text="🔁", **btn_style).grid(row=0, column=4, padx=5)
        
        # Volume control (compact)
        vol_bg = tk.Frame(inner, bg='#1a0f0a')
        vol_bg.pack(pady=10)
        
        vol_frame = tk.Frame(vol_bg, bg='#1a0f0a')
        vol_frame.pack(padx=18, pady=6)
        
        tk.Label(vol_frame, text="🔊", font=("Arial", 11),
                fg="white", bg='#1a0f0a').pack(side="left", padx=5)
        
        self.vol_slider = tk.Scale(
            vol_frame, from_=0, to=100, orient="horizontal",
            showvalue=False, bg='#1a0f0a', fg=COLORS['primary'],
            troughcolor='#0a0a0a', activebackground=COLORS['primary'],
            highlightthickness=0, bd=0, sliderlength=11,
            length=400, command=self.set_vol
        )
        self.vol_slider.set(70)
        self.vol_slider.pack(side="left")
        
        self.vol_label = tk.Label(vol_frame, text="70", 
                                 font=("Arial", 10, "bold"),
                                 fg="white", bg='#1a0f0a', width=3)
        self.vol_label.pack(side="left", padx=5)
        
        # Social buttons (compact)
        social_frame = tk.Frame(inner, bg='#2a1f1a')
        social_frame.pack(pady=10)
        
        like_color = COLORS['primary'] if self.is_liked else "white"
        self.like_btn = tk.Button(social_frame, 
                                  text="❤️" if self.is_liked else "🤍",
                                  font=("Arial", 15), 
                                  bg='#1a0f0a', 
                                  fg=like_color,
                                  bd=0, cursor="hand2", width=3, height=1,
                                  activebackground="#0a0a0a",
                                  command=self.toggle_like)
        self.like_btn.pack(side="left", padx=8)
        
        tk.Label(social_frame, text="Like", font=("Arial", 9),
                fg="#aaa", bg='#2a1f1a').pack(side="left", padx=(0, 18))
        
        tk.Button(social_frame, text="📤", font=("Arial", 15),
                 bg='#1a0f0a', fg="white", bd=0, cursor="hand2",
                 width=3, height=1,
                 activebackground="#0a0a0a",
                 command=self.show_share_menu).pack(side="left", padx=8)
        
        tk.Label(social_frame, text="Share", font=("Arial", 9),
                fg="#aaa", bg='#2a1f1a').pack(side="left")
        
        # Status label
        self.status_label = tk.Label(inner, text="", 
                                     font=("Arial", 9, "bold"),
                                     fg=COLORS['warning'], bg='#2a1f1a')
        self.status_label.pack(pady=6)

    def load_background(self):
        """Load background for music player"""
        try:
            if os.path.exists('background.jpg'):
                img = Image.open('background.jpg')
            else:
                img = self.create_gradient_background()
            
            screen_width = self.canvas.winfo_width()
            screen_height = self.canvas.winfo_height()
            
            if screen_width <= 1:
                screen_width = self.canvas.winfo_screenwidth()
            if screen_height <= 1:
                screen_height = self.canvas.winfo_screenheight()
            
            img_width, img_height = img.size
            
            scale = max(screen_width / img_width, screen_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            left = (new_width - screen_width) // 2
            top = (new_height - screen_height) // 2
            img = img.crop((left, top, left + screen_width, top + screen_height))
            
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
            
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.7)
            
            bg_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                screen_width // 2, screen_height // 2,
                image=bg_image, anchor='center'
            )
            
            return bg_image
            
        except Exception as e:
            print(f"Background error: {e}")
            self.canvas.configure(bg='#0a0a0a')
            return None

    def create_gradient_background(self):
        """Fallback gradient"""
        img = Image.new('RGB', (1920, 1080), '#0a0a0a')
        from PIL import ImageDraw
        import random
        
        draw = ImageDraw.Draw(img)
        for i in range(25):
            x = random.randint(0, 1920)
            y = random.randint(0, 1080)
            size = random.randint(80, 250)
            color = random.choice(['#E74C3C', '#f7931e', '#fdc830', '#c471f5'])
            draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
        
        img = img.filter(ImageFilter.GaussianBlur(radius=100))
        return img

    def set_default_art(self):
        try:
            img = Image.new('RGB', (216, 216), color='#0a0a0a')
            draw = ImageDraw.Draw(img)
            
            # Headphone design (centered, smaller)
            draw.ellipse([85, 95, 110, 120], fill=COLORS['primary'])
            draw.ellipse([106, 90, 131, 115], fill=COLORS['primary'])
            draw.rectangle([103, 65, 110, 108], fill=COLORS['primary'])
            draw.rectangle([128, 60, 135, 103], fill=COLORS['primary'])
            
            photo = ImageTk.PhotoImage(img)
            self.art.config(image=photo)
            self.art.image = photo
        except:
            pass

    # ==================== SEEKING FUNCTIONS ====================
    
    def on_seek_start(self, event):
        if not self.is_playing or self.downloading:
            return
        self.seeking = True

    def on_slider_move(self, value):
        if self.seeking and self.is_playing:
            new_pos = (float(value) / 100) * self.song_duration
            self.time_start.config(text=self.format_time(new_pos))

    def on_seek_end(self, event):
        if not self.is_playing or self.downloading or not self.current_audio_path:
            return
        
        try:
            percentage = self.progress_var.get()
            new_position = (percentage / 100) * self.song_duration
            
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.current_audio_path)
            pygame.mixer.music.play(start=int(new_position))
            
            self.play_start_time = time.time() - new_position
            
            if self.is_paused:
                pygame.mixer.music.pause()
                self.pause_time = new_position
            
            print(f"⏩ Seeked to {self.format_time(new_position)}")
            
        except Exception as e:
            print(f"❌ Seek error: {e}")
        finally:
            self.seeking = False

    # ==================== PLAYBACK FUNCTIONS ====================
    
    def toggle_like(self):
        current_user = get_current_user()
        if not current_user:
            return
        
        favorites = load_favorites(current_user)
        
        if self.emotion in favorites:
            del favorites[self.emotion]
            self.is_liked = False
            self.like_btn.config(text="🤍", fg="white")
            self.status_label.config(text="Removed from favorites", fg="#888")
        else:
            favorites[self.emotion] = {
                'timestamp': time.time(),
                'songs': self.songs
            }
            self.is_liked = True
            self.like_btn.config(text="❤️", fg=COLORS['primary'])
            self.status_label.config(text="Added to favorites ❤️", fg=COLORS['primary'])
        
        save_favorites(favorites, current_user)
        self.root.after(2000, lambda: self.status_label.config(text=""))

    def show_share_menu(self):
        share_window = tk.Toplevel(self.root)
        share_window.title("Share Playlist")
        share_window.geometry("600x500")
        share_window.resizable(False, False)
        share_window.configure(bg='#1a0f0a')
        
        share_window.transient(self.root)
        share_window.grab_set()
        
        share_window.update_idletasks()
        x = (share_window.winfo_screenwidth() // 2) - 300
        y = (share_window.winfo_screenheight() // 2) - 250
        share_window.geometry(f"600x500+{x}+{y}")
        
        tk.Label(share_window, text="📤 Share Playlist", 
                font=("Arial", 16, "bold"),
                fg="white", bg='#1a0f0a').pack(pady=15)
        
        # Create share text with ALL songs and YouTube links
        share_text = f"🎵 Check out my {self.emotion.upper()} playlist on EmoTune!\n\n"
        
        for i, song in enumerate(self.songs, 1):
            youtube_url = f"https://music.youtube.com/watch?v={song['id']}"
            share_text += f"{i}. {song['title']} - {song['artist']}\n   🔗 {youtube_url}\n\n"
        
        # Scrollable text area to show full playlist
        text_frame = tk.Frame(share_window, bg='#1a0f0a')
        text_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        text_widget = tk.Text(text_frame, 
                             font=("Arial", 9),
                             bg='#2a1f1a', fg='white',
                             wrap="word", height=15,
                             yscrollcommand=scrollbar.set,
                             relief="flat", bd=5)
        text_widget.pack(side="left", fill="both", expand=True)
        text_widget.insert("1.0", share_text)
        text_widget.config(state="disabled")  # Read-only
        
        scrollbar.config(command=text_widget.yview)
        
        btn_style = {
            "font": ("Arial", 11, "bold"), "width": 24, "height": 1,
            "bg": "#2a1f1a", "fg": "white", "bd": 0, "cursor": "hand2",
            "activebackground": "#3a2510"
        }
        
        btn_frame = tk.Frame(share_window, bg='#1a0f0a')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="📱 Share on WhatsApp", **btn_style,
                 command=lambda: self.share_to_whatsapp(share_text)).pack(pady=4)
        tk.Button(btn_frame, text="📘 Share on Facebook", **btn_style,
                 command=lambda: self.share_to_facebook(share_text)).pack(pady=4)
        tk.Button(btn_frame, text="🐦 Share on Twitter", **btn_style,
                 command=lambda: self.share_to_twitter(share_text)).pack(pady=4)
        tk.Button(btn_frame, text="🔗 Copy to Clipboard", **btn_style,
                 command=lambda: self.copy_to_clipboard(share_text, share_window)).pack(pady=4)
        
        tk.Button(share_window, text="Close", 
                 font=("Arial", 10, "bold"),
                 bg=COLORS['primary'], fg="white",
                 width=18, height=1, bd=0, cursor="hand2",
                 activebackground=COLORS['primary_dark'],
                 command=share_window.destroy).pack(pady=10)

    def share_to_whatsapp(self, text):
        webbrowser.open(f"https://api.whatsapp.com/send?text={urllib.parse.quote(text)}")

    def share_to_facebook(self, text):
        webbrowser.open(f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote('https://emotune.app')}&quote={urllib.parse.quote(text)}")

    def share_to_twitter(self, text):
        webbrowser.open(f"https://twitter.com/intent/tweet?text={urllib.parse.quote(text)}")

    def copy_to_clipboard(self, text, window):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_label.config(text="✅ Copied to clipboard!", fg=COLORS['success'])
        window.destroy()
        self.root.after(2000, lambda: self.status_label.config(text=""))

    def download_song(self, video_id):
        cache_path = get_cache_path(video_id)
        
        if os.path.exists(cache_path):
            self.status_label.config(text="Playing from cache", fg=COLORS['success'])
            return cache_path
        
        self.downloading = True
        self.status_label.config(text="⬇️ Downloading...", fg=COLORS['warning'])
        
        try:
            # Check if FFmpeg is available
            try:
                import subprocess
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                print("❌ ERROR: FFmpeg not installed!")
                self.status_label.config(text="❌ FFmpeg not installed", fg=COLORS['primary'])
                self.downloading = False
                return None
            
            url = f"https://music.youtube.com/watch?v={video_id}"
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': cache_path.replace('.mp3', '.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }],
                'quiet': False,  # Changed to False to see errors
                'no_warnings': False,  # Changed to False to see warnings
            }
            
            print(f"🎵 Downloading: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Wait for file to appear
            for i in range(10):
                if os.path.exists(cache_path):
                    print(f"✅ Downloaded: {cache_path}")
                    break
                time.sleep(0.5)
            
            if os.path.exists(cache_path):
                self.status_label.config(text="")
                self.downloading = False
                return cache_path
            
            raise Exception("Download completed but file not found")
            
        except Exception as e:
            print(f"❌ Download error: {str(e)}")
            print(f"❌ Video ID: {video_id}")
            print(f"❌ Cache path: {cache_path}")
            self.status_label.config(text=f"Download failed: {str(e)[:30]}", fg=COLORS['primary'])
            self.downloading = False
            return None

    def play(self):
        if self.current >= len(self.songs):
            self.current = 0
        self.load_and_play(self.songs[self.current])

    def load_and_play(self, song):
        try:
            self.song_label.config(text=song['title'][:55])
            self.artist_label.config(text=song['artist'][:45])
            self.time_end.config(text=song['duration_str'])
            self.song_duration = song['duration']
            
            self.load_thumbnail(song['id'])
            
            audio_path = self.download_song(song['id'])
            if not audio_path:
                raise Exception("Cannot get audio")
            
            self.current_audio_path = audio_path
            
            time.sleep(0.3)
            
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            self.play_start_time = time.time()
            self.is_playing = True
            self.is_paused = False
            self.play_pause_btn.config(text="⏸")
            
            self.update_progress()

        except Exception as e:
            print(f"❌ Play error: {e}")
            time.sleep(1)
            self.next()

    def load_thumbnail(self, video_id):
        try:
            url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content)).resize((216, 216))
                mask = Image.new('L', (216, 216), 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle([(0, 0), (216, 216)], radius=10, fill=255)
                img.putalpha(mask)
                photo = ImageTk.PhotoImage(img)
                self.art.config(image=photo)
                self.art.image = photo
        except:
            self.set_default_art()

    def play_pause(self):
        if self.downloading:
            return
        if self.is_playing:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.play_start_time = time.time() - self.pause_time
                self.is_paused = False
                self.play_pause_btn.config(text="⏸")
            else:
                pygame.mixer.music.pause()
                self.pause_time = time.time() - self.play_start_time
                self.is_paused = True
                self.play_pause_btn.config(text="▶")
        else:
            threading.Thread(target=self.play, daemon=True).start()

    def next(self):
        if self.downloading:
            return
        pygame.mixer.music.stop()
        self.is_playing = False
        self.current = (self.current + 1) % len(self.songs)
        threading.Thread(target=self.play, daemon=True).start()

    def previous(self):
        if self.downloading:
            return
        pygame.mixer.music.stop()
        self.is_playing = False
        self.current = (self.current - 1) % len(self.songs)
        threading.Thread(target=self.play, daemon=True).start()

    def set_vol(self, val):
        volume = int(val)
        pygame.mixer.music.set_volume(volume / 100)
        self.vol_label.config(text=str(volume))

    def update_progress(self):
        if not self.is_running:
            return
            
        if self.is_playing:
            try:
                if pygame.mixer.music.get_busy() or self.is_paused:
                    if not self.seeking:
                        if self.is_paused:
                            pos = self.pause_time
                        else:
                            pos = time.time() - self.play_start_time
                        
                        self.time_start.config(text=self.format_time(pos))
                        
                        if self.song_duration > 0:
                            percent = (pos / self.song_duration) * 100
                            self.progress_var.set(min(percent, 100))
                else:
                    if not self.is_paused and not self.downloading:
                        self.next()
                        return
            except tk.TclError:
                self.is_running = False
                return
            except:
                pass
        
        if self.is_running:
            try:
                self.update_id = self.root.after(100, self.update_progress)
            except tk.TclError:
                self.is_running = False

    def format_time(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"

    def go_back(self):
        """Go back - NO FLICKER"""
        # Stop music first
        self.is_running = False
        
        try:
            pygame.mixer.music.stop()
        except:
            pass
        
        # Hide window
        self.root.withdraw()
        self.root.update_idletasks()
        self.root.after(5, self._complete_go_back)
    
    def _complete_go_back(self):
        """Complete go back"""
        try:
            # Cancel any pending updates
            if self.update_id:
                try:
                    self.root.after_cancel(self.update_id)
                except:
                    pass
            
            # Stop pygame
            try:
                pygame.mixer.quit()
            except:
                pass
            
            # Destroy window
            self.root.quit()
            self.root.destroy()
            
            # Call parent callback
            if self.parent_callback:
                self.parent_callback()
        except Exception as e:
            print(f"Error going back: {e}")

    def on_closing(self):
        self.cleanup()

    def cleanup(self):
        self.is_running = False
        
        if self.update_id:
            try:
                self.root.after_cancel(self.update_id)
            except:
                pass
        
        try:
            pygame.mixer.music.stop()
        except:
            pass
        
        try:
            self.root.destroy()
        except:
            pass