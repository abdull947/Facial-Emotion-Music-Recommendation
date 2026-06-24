# ui_components.py
import tkinter as tk
from tkinter import messagebox
import cv2
import time
import os
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
from ytmusicapi import YTMusic
from utils import *
from config import *
from music_player import MusicPlayer

ytmusic = YTMusic()

def load_background_image(canvas, blur=2, brightness=0.75):
    """Load centered background - MORE VISIBLE"""
    try:
        if os.path.exists('background.jpg'):
            img = Image.open('background.jpg')
        else:
            img = create_gradient_bg()
        
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        
        if w <= 1:
            w = canvas.winfo_screenwidth()
        if h <= 1:
            h = canvas.winfo_screenheight()
        
        iw, ih = img.size
        scale = max(w / iw, h / ih)
        nw = int(iw * scale)
        nh = int(ih * scale)
        
        img = img.resize((nw, nh), Image.Resampling.LANCZOS)
        
        left = (nw - w) // 2
        top = (nh - h) // 2
        img = img.crop((left, top, left + w, top + h))
        
        img = img.filter(ImageFilter.GaussianBlur(radius=blur))
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness)
        
        bg_img = ImageTk.PhotoImage(img)
        canvas.create_image(w // 2, h // 2, image=bg_img, anchor='center')
        
        return bg_img
    except Exception as e:
        print(f"BG error: {e}")
        canvas.configure(bg='#0a0a0a')
        return None

def create_gradient_bg():
    """Fallback gradient"""
    img = Image.new('RGB', (1920, 1080), '#0a0a0a')
    from PIL import ImageDraw
    import random
    
    draw = ImageDraw.Draw(img)
    for i in range(30):
        x = random.randint(0, 1920)
        y = random.randint(0, 1080)
        size = random.randint(100, 300)
        color = random.choice(['#ff6b35', '#f7931e', '#fdc830', '#c471f5', '#E74C3C'])
        draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
    
    img = img.filter(ImageFilter.GaussianBlur(radius=120))
    return img

# ==================== HOME PAGE ====================
class HomePage:
    def __init__(self, username=None):
        self.root = tk.Tk()
        self.root.title("EmoTune")
        
        # CRITICAL: Hide window immediately to prevent flicker
        self.root.withdraw()
        
        self.root.state('zoomed')
        self.root.configure(bg='black')
        
        # Set current user if provided
        if username:
            set_current_user(username)
        
        self.current_user = get_current_user()
        self.root.update_idletasks()
        
        self.create_ui()
        
        # CRITICAL: Show window only after UI is complete
        self.root.deiconify()
        
        self.root.mainloop()

    def create_ui(self):
        # Canvas
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='black')
        self.canvas.pack(fill="both", expand=True)
        self.canvas.update()
        
        # Background
        self.bg_image = load_background_image(self.canvas, blur=2, brightness=0.75)
        
        # SMALLER User bar (height reduced to 45)
        user_bar = tk.Frame(self.canvas, bg='#1a0f0a', height=45)
        user_bar_win = self.canvas.create_window(
            self.canvas.winfo_width() // 2, 23,
            window=user_bar, width=self.canvas.winfo_width(), height=45
        )
        
        tk.Label(user_bar, text=f"👤 {self.current_user}", 
                font=("Arial", 11, "bold"),
                fg='white', bg='#1a0f0a').pack(side="left", padx=20, pady=10)
        
        tk.Button(user_bar, text="🚪 Logout", 
                 font=("Arial", 10, "bold"),
                 bg=COLORS['primary'], fg="white",
                 bd=0, cursor="hand2", padx=15, pady=5,
                 activebackground=COLORS['primary_dark'],
                 command=self.logout).pack(side="right", padx=20, pady=10)
        
        # LEFT-ALIGNED content container (35% from left)
        screen_width = self.canvas.winfo_width()
        screen_height = self.canvas.winfo_height()
        left_x = int(screen_width * 0.35)
        center_y = int(screen_height * 0.52)  # Slightly below center
        
        # Brown-tinted container
        content = tk.Frame(self.canvas, bg='#2a1f1a', width=420, height=550)
        content_win = self.canvas.create_window(
            left_x, center_y,
            window=content, anchor='center'
        )
        content.pack_propagate(False)
        
        def update_pos(e=None):
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            
            lx = int(w * 0.35)
            cy = int(h * 0.52)
            
            self.canvas.coords(user_bar_win, w // 2, 23)
            self.canvas.itemconfig(user_bar_win, width=w)
            self.canvas.coords(content_win, lx, cy)
        
        self.root.bind('<Configure>', update_pos)
        
        # Inner content
        inner = tk.Frame(content, bg='#2a1f1a')
        inner.pack(expand=True, pady=15)
        
        # Logo (smaller)
        tk.Label(inner, text="🎵", font=("Arial", 40),
                fg=COLORS['primary'], bg='#2a1f1a').pack(pady=(6, 4))
        
        tk.Label(inner, text="EmoTune", 
                font=("Helvetica", 34, "bold"),
                fg=COLORS['primary'], bg='#2a1f1a').pack(pady=4)
        
        tk.Label(inner, text="AI-Powered Emotion Music Player", 
                font=("Arial", 12),
                fg='white', bg='#2a1f1a').pack(pady=3)
        
        tk.Label(inner, text="Detects your mood and plays perfect music", 
                font=("Arial", 10),
                fg='#ccc', bg='#2a1f1a').pack(pady=3)
        
        # Buttons
        btn_frame = tk.Frame(inner, bg='#2a1f1a')
        btn_frame.pack(pady=30)
        
        tk.Button(btn_frame, text="🎭 Start Detection", 
                 font=("Arial", 13, "bold"),
                 bg=COLORS['primary'], fg="white",
                 width=20, height=2, bd=0, cursor="hand2",
                 activebackground=COLORS['primary_dark'],
                 command=self.start_detection).pack(pady=8)
        
        tk.Button(btn_frame, text="📜 View History", 
                 font=("Arial", 12, "bold"),
                 bg='#3a2510', fg="white",
                 width=20, height=2, bd=0, cursor="hand2",
                 activebackground="#2a1510",
                 command=self.view_history).pack(pady=8)
        
        # Settings button
        tk.Button(btn_frame, text="⚙️ Settings", 
                font=("Arial", 12, "bold"),
                bg='#3a2510', fg="white",
                width=20, height=2, bd=0, cursor="hand2",
                activebackground="#2a1510",
                command=self.open_settings).pack(pady=8)

        # Statistics button
        tk.Button(btn_frame, text="📊 Statistics", 
                font=("Arial", 12, "bold"),
                bg='#3a2510', fg="white",
                width=20, height=2, bd=0, cursor="hand2",
                activebackground="#2a1510",
                command=self.open_statistics).pack(pady=8)


    def start_detection(self):
        """Navigate to detection - NO FLICKER"""
        self.root.withdraw()
        self.root.update_idletasks()
        self.root.after(5, self._launch_detection)
    
    def _launch_detection(self):
        """Complete detection launch"""
        try:
            self.root.quit()
            self.root.destroy()
            WebcamPage(self.restart_home)
        except Exception as e:
            print(f"Error launching detection: {e}")

    def view_history(self):
        """Navigate to history - NO FLICKER"""
        self.root.withdraw()
        self.root.update_idletasks()
        self.root.after(5, self._launch_history)
    
    def _launch_history(self):
        """Complete history launch"""
        try:
            self.root.quit()
            self.root.destroy()
            HistoryViewer(self.restart_home)
        except Exception as e:
            print(f"Error launching history: {e}")

    def open_settings(self):
        """Navigate to settings - NO FLICKER"""
        self.root.withdraw()
        self.root.update_idletasks()
        self.root.after(5, self._launch_settings)

    def _launch_settings(self):
        """Complete settings launch"""
        try:
            from settings_page import SettingsPage
            
            self.root.quit()
            self.root.destroy()
            
            SettingsPage(self.restart_home)
        except Exception as e:
            print(f"Error launching settings: {e}")

    def open_statistics(self):
        """Navigate to statistics - NO FLICKER"""
        self.root.withdraw()
        self.root.update_idletasks()
        self.root.after(5, self._launch_statistics)

    def _launch_statistics(self):
        """Complete statistics launch"""
        try:
            from statistics_page import StatisticsPage
            
            self.root.quit()
            self.root.destroy()
            
            StatisticsPage(self.restart_home)
        except Exception as e:
            print(f"Error launching statistics: {e}")

    def logout(self):
        """Logout - NO FLICKER"""
        if messagebox.askyesno("Logout", "Are you sure?"):
            logout_user()
            self.root.withdraw()
            self.root.update_idletasks()
            self.root.after(5, self._do_logout)
    
    def _do_logout(self):
        """Complete logout"""
        try:
            self.root.quit()
            self.root.destroy()
            from auth import AuthPage
            AuthPage()
        except Exception as e:
            print(f"Error during logout: {e}")

    def restart_home(self):
        HomePage()

# ==================== WEBCAM PAGE ====================
class WebcamPage:
    def __init__(self, parent_callback=None):
        self.root = tk.Tk()
        self.root.title("EmoTune - Detection")
        
        # CRITICAL: Hide window immediately to prevent flicker
        self.root.withdraw()
        
        self.root.state('zoomed')
        self.root.configure(bg='black')
        
        self.parent_callback = parent_callback
        self.is_running = True
        self.update_id = None
        self.captured = False
        self.hold_start = None
        
        self.root.update_idletasks()
        self.create_ui()
        
        self.cap = cv2.VideoCapture(0)
        self.detector = DETECTOR
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # CRITICAL: Show window only after everything is ready
        self.root.deiconify()
        
        self.update_frame()
        self.root.mainloop()

    def create_ui(self):
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='black')
        self.canvas.pack(fill="both", expand=True)
        self.canvas.update()
        
        self.bg_image = load_background_image(self.canvas, blur=3, brightness=0.7)
        
        # Smaller top bar (height 50)
        top_bar = tk.Frame(self.canvas, bg='#1a0f0a', height=50)
        top_bar_win = self.canvas.create_window(
            self.canvas.winfo_width() // 2, 25,
            window=top_bar, width=self.canvas.winfo_width(), height=50
        )
        
        tk.Button(top_bar, text="←", font=("Arial", 18, "bold"),
                 fg="white", bg='#1a0f0a', bd=0, cursor="hand2",
                 activebackground='#2a1510',
                 command=self.go_back).pack(side="left", padx=12)
        
        tk.Label(top_bar, text="🎵 Emotion Detection", 
                font=("Arial", 16, "bold"),
                fg="white", bg='#1a0f0a').pack(side="left", expand=True)
        
        # Camera
        cam_frame = tk.Frame(self.canvas, bg='#2a1f1a', bd=2, relief="solid")
        cam_win = self.canvas.create_window(
            self.canvas.winfo_width() // 2,
            self.canvas.winfo_height() // 2,
            window=cam_frame, anchor='center'
        )
        
        self.cam_label = tk.Label(cam_frame, bg="black")
        self.cam_label.pack(padx=4, pady=4)
        
        # Progress
        progress_frame = tk.Frame(self.canvas, bg='#2a1f1a')
        progress_win = self.canvas.create_window(
            self.canvas.winfo_width() // 2,
            self.canvas.winfo_height() - 70,
            window=progress_frame
        )
        
        self.progress = tk.Label(progress_frame, text="Ready! Position your face...", 
                                font=("Arial", 12, "bold"), fg="white", bg='#2a1f1a',
                                padx=20, pady=10)
        self.progress.pack()
        
        def update_pos(e=None):
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            self.canvas.coords(top_bar_win, w // 2, 25)
            self.canvas.itemconfig(top_bar_win, width=w)
            self.canvas.coords(cam_win, w // 2, h // 2 + 10)
            self.canvas.coords(progress_win, w // 2, h - 70)
        
        self.root.bind('<Configure>', update_pos)

    def update_frame(self):
        if not self.is_running:
            return
        
        try:
            ret, frame = self.cap.read()
            if not ret:
                if self.is_running:
                    self.update_id = self.root.after(10, self.update_frame)
                return

            frame = cv2.resize(frame, (800, 500))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, 
                                                       minSize=(MIN_FACE_SIZE, MIN_FACE_SIZE))

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (231, 76, 60), 5)

            if len(faces) > 0:
                face_img = frame[faces[0][1]:faces[0][1]+faces[0][3], 
                                faces[0][0]:faces[0][0]+faces[0][2]]

                try:
                    emotion, score = self.detector.top_emotion(face_img)
                    if emotion and score > CONFIDENCE_THRESHOLD:
                        if self.hold_start is None:
                            self.hold_start = time.time()
                        
                        elapsed = time.time() - self.hold_start
                        bar_length = int(elapsed / CAPTURE_HOLD_TIME * 35)
                        bar = "█" * bar_length + "░" * (35 - bar_length)
                        self.progress.config(
                            text=f"Analyzing {emotion.upper()}... {bar} {elapsed:.1f}s",
                            fg=COLORS['emotions'].get(emotion.lower(), 'white'))

                        if elapsed >= CAPTURE_HOLD_TIME and not self.captured:
                            self.captured = True
                            print(f"\n😊 {emotion.upper()} ({score:.1%})\n")
                            
                            face_path = f"{FACES_FOLDER}/face_{int(time.time())}.jpg"
                            cv2.imwrite(face_path, frame)
                            
                            songs = get_cached_or_search(emotion, ytmusic)
                            
                            if songs:
                                 # ========== SAVE HISTORY SETTING CHECK ==========
                                current_user = get_current_user()
                                settings = settings_collection.find_one({'username': current_user})
                                
                                # Get save_history setting (default is True if not set)
                                should_save = True
                                if settings:
                                    should_save = settings.get('save_history', True)
                                
                                if should_save:
                                    add_to_history(emotion, score, face_path, songs)
                                    print(f"✅ History saved for {current_user}")
                                else:
                                    print(f"⏭️ History saving disabled for {current_user}")
                                
                                # Flicker-free transition to music player
                                self.is_running = False
                                if hasattr(self, 'cap') and self.cap:
                                    try:
                                        self.cap.release()
                                    except:
                                        pass
                                
                                self.root.withdraw()
                                self.root.update_idletasks()
                                self.root.after(5, lambda: self._launch_music_player(emotion, songs))
                            else:
                                messagebox.showerror("Error", "No songs found")
                                self.reset_capture()
                    else:
                        self.progress.config(text="Hold still...", fg='white', bg='#2a1f1a')
                        self.hold_start = None
                except Exception as e:
                    print(f"Error: {e}")
                    self.progress.config(text="Try again...", fg='#ff4444', bg='#2a1f1a')
                    self.hold_start = None
            else:
                self.progress.config(text="No face! Move closer...", fg='#ffaa00', bg='#2a1f1a')
                self.hold_start = None

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(img)
            self.cam_label.config(image=photo)
            self.cam_label.image = photo

        except tk.TclError:
            self.is_running = False
            return
        except Exception as e:
            print(f"Frame error: {e}")

        if self.is_running:
            try:
                self.update_id = self.root.after(10, self.update_frame)
            except tk.TclError:
                self.is_running = False

    def reset_capture(self):
        self.captured = False
        self.hold_start = None

    def go_back(self):
        """Go back - NO FLICKER"""
        # Stop camera first
        self.is_running = False
        if hasattr(self, 'cap') and self.cap:
            try:
                self.cap.release()
            except:
                pass
        
        # Hide window
        self.root.withdraw()
        self.root.update_idletasks()
        self.root.after(5, self._complete_go_back)
    
    def _complete_go_back(self):
        """Complete go back"""
        try:
            if self.update_id:
                try:
                    self.root.after_cancel(self.update_id)
                except:
                    pass
            
            self.root.quit()
            self.root.destroy()
            
            if self.parent_callback:
                self.parent_callback()
        except Exception as e:
            print(f"Error going back: {e}")

    def on_closing(self):
        self.cleanup()
    def _launch_music_player(self, emotion, songs):
        """Complete music player launch - NO FLICKER - WITH AUTO-PLAY CHECK"""
        try:
            if self.update_id:
                try:
                    self.root.after_cancel(self.update_id)
                except:
                    pass
            
            self.root.quit()
            self.root.destroy()
            
            # ========== AUTO-PLAY SETTING CHECK ==========
            from tkinter import messagebox as msg
            
            current_user = get_current_user()
            settings = settings_collection.find_one({'username': current_user})
            
            # Get auto_play setting (default is True if not set)
            auto_play = True
            if settings:
                auto_play = settings.get('auto_play', True)
            
            if auto_play:
                # Auto-play is ON - launch music player immediately
                MusicPlayer(emotion, songs, self.parent_callback)
            else:
                # Auto-play is OFF - ask user first
                root = tk.Tk()
                root.withdraw()  # Hide the root window
                
                play = msg.askyesno(
                    "Play Music?", 
                    f"✅ Detected: {emotion.upper()}\n\n🎵 Play music now?",
                    icon='question'
                )
                
                root.destroy()
                
                if play:
                    MusicPlayer(emotion, songs, self.parent_callback)
                else:
                    # User declined - go back to home
                    if self.parent_callback:
                        self.parent_callback()
                    else:
                        HomePage()
            # =============================================
        except Exception as e:
            print(f"Error launching music player: {e}")

    def cleanup(self):
        self.is_running = False
        if self.update_id:
            try:
                self.root.after_cancel(self.update_id)
            except:
                pass
        try:
            self.cap.release()
        except:
            pass
        try:
            self.root.destroy()
        except:
            pass

# ==================== HISTORY VIEWER ====================
class HistoryViewer:
    def __init__(self, parent_callback=None):
        self.root = tk.Tk()
        self.root.title("EmoTune - History")
        
        # CRITICAL: Hide window immediately to prevent flicker
        self.root.withdraw()
        
        self.root.state('zoomed')
        self.root.configure(bg='black')
        
        self.parent_callback = parent_callback
        self.current_user = get_current_user()
        
        self.root.update_idletasks()
        self.create_ui()
        
        # CRITICAL: Show window only after UI is complete
        self.root.deiconify()
        
        self.root.mainloop()

    def create_ui(self):
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='black')
        self.canvas.pack(fill="both", expand=True)
        self.canvas.update()
        
        self.bg_image = load_background_image(self.canvas, blur=2, brightness=0.75)
        
        # Top bar
        top_bar = tk.Frame(self.canvas, bg='#1a0f0a', height=45)
        top_bar_win = self.canvas.create_window(
            self.canvas.winfo_width() // 2, 23,
            window=top_bar, width=self.canvas.winfo_width(), height=45
        )
        
        tk.Button(top_bar, text="←", font=("Arial", 18, "bold"),
                 fg="white", bg='#1a0f0a', bd=0, cursor="hand2",
                 activebackground='#2a1510',
                 command=self.go_back).pack(side="left", padx=12)
        
        tk.Label(top_bar, text=f"📜 {self.current_user}'s History", 
                font=("Arial", 16, "bold"),
                fg="white", bg='#1a0f0a').pack(side="left", expand=True)
        
        tk.Button(top_bar, text="🗑️ Clear", 
                 font=("Arial", 10, "bold"),
                 fg="white", bg=COLORS['primary'], bd=0, cursor="hand2",
                 padx=12, pady=5,
                 activebackground=COLORS['primary_dark'],
                 command=self.clear_all).pack(side="right", padx=12)
        
        # Get screen dimensions
        screen_width = self.canvas.winfo_width()
        screen_height = self.canvas.winfo_height()

        # LEFT POSITION - 35% from left (like login page)
        left_x = int(screen_width * 0.35)
        center_y = screen_height // 2 + 20
        
        # FIXED WIDTH - 700 pixels (adjust this number to make narrower/wider)
        self.container_width = 700  # Change this to adjust width
        available_height = screen_height - 80
        
        # Main container frame
        main_container = tk.Frame(self.canvas, bg='#1a0f0a', 
                                 width=self.container_width, 
                                 height=available_height,
                                 highlightthickness=1,
                                 highlightbackground='#3a2510')
        
        container_win = self.canvas.create_window(
            left_x,  # LEFT position instead of center
            center_y,
            window=main_container, 
            anchor='center'
        )
        
        # CRITICAL: Prevent frame from resizing
        main_container.pack_propagate(False)
        main_container.grid_propagate(False)
        
        def update_pos(e=None):
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            
            # Maintain left position at 35%
            lx = int(w * 0.35)
            cy = h // 2 + 20
            avail_h = h - 80
            
            self.canvas.coords(top_bar_win, w // 2, 23)
            self.canvas.itemconfig(top_bar_win, width=w)
            
            self.canvas.coords(container_win, w // 2, h // 2 + 20)
            # Update to left position
            self.canvas.coords(container_win, lx, cy)
            main_container.config(height=avail_h)
        
        self.root.bind('<Configure>', update_pos)
        
        # Scrollable canvas inside container
        scroll_canvas = tk.Canvas(main_container, 
                                 bg='#1a0f0a', 
                                 highlightthickness=0,
                                 width=self.container_width - 20)  # Account for scrollbar
        
        scrollbar = tk.Scrollbar(main_container, 
                               orient="vertical", 
                               command=scroll_canvas.yview,
                               bg='#3a2510', 
                               troughcolor='#1a0f0a', 
                               activebackground='#4a3520', 
                               width=15)
        
        # Frame that holds all history cards
        scrollable_frame = tk.Frame(scroll_canvas, bg='#1a0f0a')
        
        # Update scroll region when content changes
        scrollable_frame.bind("<Configure>",
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))
        
        scroll_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=self.container_width - 20)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        scroll_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Load history
        history = load_history(self.current_user)
        
        if not history:
            tk.Label(scrollable_frame, 
                    text="No history yet\n\nStart detecting emotions!",
                    font=("Arial", 14), fg="#aaa", bg='#1a0f0a',
                    justify="center").pack(pady=150)
        else:
            for entry in history:
                self.create_entry(scrollable_frame, entry)

    def create_entry(self, parent, entry):
        # Card fills the scrollable frame width
        card = tk.Frame(parent, bg='#2a1f1a', bd=0)
        card.pack(fill="x", pady=6, padx=8)
        
        emotion_color = COLORS['emotions'].get(entry['emotion'].lower(), COLORS['primary'])
        
        # Top accent bar
        tk.Frame(card, bg=emotion_color, height=4).pack(fill="x")
        
        # Content
        content = tk.Frame(card, bg='#2a1f1a')
        content.pack(fill="x", padx=18, pady=12)
        
        # Header row
        header = tk.Frame(content, bg='#2a1f1a')
        header.pack(fill="x", pady=(0, 8))
        
        # Emotion + Confidence
        left_side = tk.Frame(header, bg='#2a1f1a')
        left_side.pack(side="left")
        
        tk.Label(left_side, text=f"😊 {entry['emotion'].upper()}", 
                font=("Arial", 14, "bold"),
                fg=emotion_color, bg='#2a1f1a').pack(side="left")
        
        tk.Label(left_side, text=f"  {entry['confidence']:.0%}", 
                font=("Arial", 11), fg="#bbb", bg='#2a1f1a').pack(side="left", padx=10)
        
        # Date
        tk.Label(header, text=entry['date_formatted'], 
                font=("Arial", 9), fg="#888", bg='#2a1f1a').pack(side="right")
        
        # Songs section
        songs_section = tk.Frame(content, bg='#2a1f1a')
        songs_section.pack(fill="x", pady=6)
        
        tk.Label(songs_section, text=f"🎵 {len(entry['songs'])} songs", 
                font=("Arial", 11, "bold"),
                fg="white", bg='#2a1f1a').pack(anchor="w", pady=(0, 5))
        
        # Song list
        for i, song in enumerate(entry['songs'][:5], 1):
            song_row = tk.Frame(songs_section, bg='#2a1f1a')
            song_row.pack(fill="x", pady=2)
            
            tk.Label(song_row, text=f"{i}.", 
                    font=("Arial", 9, "bold"), 
                    fg='#666', bg='#2a1f1a').pack(side="left", padx=(2, 6))
            
            tk.Label(song_row, text=song['title'][:70] + "...", 
                    font=("Arial", 9), 
                    fg='#ddd', bg='#2a1f1a',
                    anchor="w").pack(side="left", fill="x", expand=True)
        
        if len(entry['songs']) > 5:
            tk.Label(songs_section, text=f"... +{len(entry['songs']) - 5} more", 
                    font=("Arial", 9, "italic"),
                    fg="#888", bg='#2a1f1a').pack(anchor="w", padx=8, pady=2)
        
        # Replay button
        tk.Button(content, text="🔁 Replay Session", 
                 font=("Arial", 10, "bold"),
                 bg=COLORS['primary'], fg="white", 
                 bd=0, cursor="hand2",
                 padx=18, pady=7,
                 activebackground=COLORS['primary_dark'],
                 command=lambda e=entry: self.replay(e)).pack(anchor="w", pady=(8, 0))

    def replay(self, entry):
        """Replay session - NO FLICKER"""
        self.root.withdraw()
        self.root.update_idletasks()
        self.root.after(5, lambda: self._launch_replay(entry))
    
    def _launch_replay(self, entry):
        """Complete replay launch"""
        try:
            self.root.quit()
            self.root.destroy()
            
            MusicPlayer(entry['emotion'], entry['songs'], self.parent_callback)
        except Exception as e:
            print(f"Error launching replay: {e}")

    def clear_all(self):
        """Clear history - NO FLICKER"""
        if messagebox.askyesno("Clear History", "Delete all history?"):
            clear_history(self.current_user)
            self.root.withdraw()
            self.root.update_idletasks()
            self.root.after(5, self._complete_clear)
    
    def _complete_clear(self):
        """Complete clear and refresh"""
        try:
            self.root.quit()
            self.root.destroy()
            HistoryViewer(self.parent_callback)
        except Exception as e:
            print(f"Error refreshing history: {e}")

    def go_back(self):
        """Go back - NO FLICKER"""
        self.root.withdraw()
        self.root.update_idletasks()
        self.root.after(5, self._complete_go_back)
    
    def _complete_go_back(self):
        """Complete go back"""
        try:
            self.root.quit()
            self.root.destroy()
            
            if self.parent_callback:
                self.parent_callback()
        except Exception as e:
            print(f"Error going back: {e}")