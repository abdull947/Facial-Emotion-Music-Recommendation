"""
statistics_page.py - User Statistics Dashboard
Features: Emotion charts, listening stats, top songs, activity calendar, streaks
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import os
from datetime import datetime, timedelta
from collections import Counter
from utils import *
from config import *

# Import matplotlib for charts
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class StatisticsPage:
    def __init__(self, parent_callback=None):
        self.root = tk.Tk()
        self.root.title("EmoTune - Statistics")
        
        # CRITICAL: Hide window immediately
        self.root.withdraw()
        
        self.root.state('zoomed')
        self.root.configure(bg='black')
        
        self.parent_callback = parent_callback
        self.current_user = get_current_user()
        
        # Load user statistics
        self.history = load_history(self.current_user)
        self.stats = self.calculate_statistics()
        
        self.root.update_idletasks()
        self.create_ui()
        
        # CRITICAL: Show window only after complete
        self.root.deiconify()
        
        self.root.mainloop()
    
    def calculate_statistics(self):
        """Calculate all statistics from history"""
        stats = {
            'total_sessions': len(self.history),
            'emotions_count': {},
            'listening_time': {},
            'top_songs': [],
            'accuracy': [],
            'streak': 0,
            'weekly_activity': {},
            'monthly_activity': {}
        }
        
        if not self.history:
            return stats
        
        # Emotion distribution
        emotions = [entry['emotion'] for entry in self.history]
        stats['emotions_count'] = dict(Counter(emotions))
        
        # Listening time per emotion (estimate: 3 min per song average)
        for entry in self.history:
            emotion = entry['emotion']
            songs_count = len(entry.get('songs', []))
            time_minutes = songs_count * 3  # Average song duration
            
            if emotion in stats['listening_time']:
                stats['listening_time'][emotion] += time_minutes
            else:
                stats['listening_time'][emotion] = time_minutes
        
        # Top songs (count occurrences)
        all_songs = []
        for entry in self.history:
            for song in entry.get('songs', []):
                all_songs.append(song.get('title', 'Unknown'))
        
        song_counter = Counter(all_songs)
        stats['top_songs'] = song_counter.most_common(10)
        
        # Accuracy (confidence scores)
        stats['accuracy'] = [entry.get('confidence', 0) * 100 for entry in self.history]
        
        # Calculate streak
        stats['streak'] = self.calculate_streak()
        
        # Weekly and monthly activity
        stats['weekly_activity'] = self.get_weekly_activity()
        stats['monthly_activity'] = self.get_monthly_activity()
        
        return stats
    
    def calculate_streak(self):
        """Calculate consecutive days of app usage"""
        if not self.history:
            return 0
        
        # Get unique dates
        dates = set()
        for entry in self.history:
            timestamp = entry.get('timestamp')
            if isinstance(timestamp, datetime):
                dates.add(timestamp.date())
        
        if not dates:
            return 0
        
        # Sort dates
        sorted_dates = sorted(dates, reverse=True)
        
        # Calculate streak from today
        today = datetime.now().date()
        streak = 0
        current_date = today
        
        for date in sorted_dates:
            if date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            elif (current_date - date).days == 1:
                streak += 1
                current_date = date - timedelta(days=1)
            else:
                break
        
        return streak
    
    def get_weekly_activity(self):
        """Get activity for past 7 days"""
        activity = {i: 0 for i in range(7)}  # 0 = today, 6 = 6 days ago
        
        today = datetime.now().date()
        
        for entry in self.history:
            timestamp = entry.get('timestamp')
            if isinstance(timestamp, datetime):
                days_ago = (today - timestamp.date()).days
                if 0 <= days_ago < 7:
                    activity[days_ago] += 1
        
        return activity
    
    def get_monthly_activity(self):
        """Get activity for past 30 days"""
        activity = {i: 0 for i in range(30)}
        
        today = datetime.now().date()
        
        for entry in self.history:
            timestamp = entry.get('timestamp')
            if isinstance(timestamp, datetime):
                days_ago = (today - timestamp.date()).days
                if 0 <= days_ago < 30:
                    activity[days_ago] += 1
        
        return activity
    
    def create_ui(self):
        # Canvas
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='black')
        self.canvas.pack(fill="both", expand=True)
        self.canvas.update()
        
        # Background
        self.bg_image = self.load_background()
        
        # Top bar
        top_bar = tk.Frame(self.canvas, bg='#1a0f0a', height=50)
        self.top_bar_win = self.canvas.create_window(
            self.canvas.winfo_width() // 2, 25,
            window=top_bar, width=self.canvas.winfo_width(), height=50
        )
        
        tk.Button(top_bar, text="←", font=("Arial", 18, "bold"),
                 fg="white", bg='#1a0f0a', bd=0, cursor="hand2",
                 activebackground='#2a1510',
                 command=self.go_back).pack(side="left", padx=12)
        
        tk.Label(top_bar, text="📊 Statistics Dashboard", 
                font=("Arial", 16, "bold"),
                fg=COLORS['primary'], bg='#1a0f0a').pack(side="left", expand=True)
        
        # Main container - FIXED WIDTH
        screen_width = self.canvas.winfo_width()
        screen_height = self.canvas.winfo_height()
        
        container_width = 1100  # Wider for charts
        
        main_container = tk.Frame(self.canvas, bg='#1a0f0a')
        self.main_win = self.canvas.create_window(
            screen_width // 2,
            screen_height // 2 + 40,
            window=main_container, anchor='center'
        )
        
        # Scrollable frame with fixed width
        scroll_canvas = tk.Canvas(main_container, bg='#1a0f0a', 
                                  highlightthickness=0, 
                                  width=container_width, 
                                  height=630)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", 
                                command=scroll_canvas.yview, width=15)
        scrollable_frame = tk.Frame(scroll_canvas, bg='#1a0f0a', width=container_width)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        )
        
        scroll_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=container_width)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        
        scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        scroll_canvas.bind("<Enter>", lambda e: scroll_canvas.bind_all("<MouseWheel>", on_mousewheel))
        scroll_canvas.bind("<Leave>", lambda e: scroll_canvas.unbind_all("<MouseWheel>"))
        
        if not self.history:
            # No data message
            tk.Label(scrollable_frame, 
                    text="📊 No Statistics Available",
                    font=("Arial", 20, "bold"),
                    fg='white', bg='#1a0f0a').pack(pady=50)
            
            tk.Label(scrollable_frame,
                    text="Start using emotion detection to see your statistics!",
                    font=("Arial", 14),
                    fg='#888', bg='#1a0f0a').pack(pady=10)
        else:
            # Overview cards
            self.create_overview_cards(scrollable_frame)
            
            # Charts row 1
            charts_row1 = tk.Frame(scrollable_frame, bg='#1a0f0a')
            charts_row1.pack(fill="x", padx=20, pady=10)
            
            # Emotion pie chart
            self.create_emotion_pie_chart(charts_row1)
            
            # Listening time bar chart
            self.create_listening_time_chart(charts_row1)
            
            # Top songs section
            self.create_top_songs_section(scrollable_frame)
            
            # Activity charts
            self.create_activity_charts(scrollable_frame)
            
            # Accuracy chart
            self.create_accuracy_chart(scrollable_frame)
        
        # Resize handler
        def update_pos(e=None):
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            self.canvas.coords(self.top_bar_win, w // 2, 25)
            self.canvas.itemconfig(self.top_bar_win, width=w)
            self.canvas.coords(self.main_win, w // 2, h // 2 + 40)
        
        self.root.bind('<Configure>', update_pos)
    
    def create_overview_cards(self, parent):
        """Create overview stat cards"""
        cards_frame = tk.Frame(parent, bg='#1a0f0a')
        cards_frame.pack(fill="x", padx=18, pady=15)
        
        # Total sessions card
        self.create_stat_card(cards_frame, "🎵", "Total Sessions",
                             str(self.stats['total_sessions']), 0)
        
        # Streak card
        self.create_stat_card(cards_frame, "🔥", "Day Streak",
                             f"{self.stats['streak']} days", 1)
        
        # Most common emotion
        if self.stats['emotions_count']:
            most_common = max(self.stats['emotions_count'], 
                            key=self.stats['emotions_count'].get)
            emoji_map = {'happy': '😊', 'sad': '😢', 'angry': '😠',
                        'fear': '😨', 'surprise': '😲', 'disgust': '🤢',
                        'neutral': '😐'}
            emoji = emoji_map.get(most_common.lower(), '😊')
            self.create_stat_card(cards_frame, emoji, "Most Common",
                                most_common.capitalize(), 2)
        
        # Avg accuracy
        if self.stats['accuracy']:
            avg_acc = sum(self.stats['accuracy']) / len(self.stats['accuracy'])
            self.create_stat_card(cards_frame, "🎯", "Avg Accuracy",
                                f"{avg_acc:.1f}%", 3)
    
    def create_stat_card(self, parent, icon, title, value, col):
        """Create a stat card"""
        card = tk.Frame(parent, bg='#2a1f1a', bd=2, relief="solid")
        card.grid(row=0, column=col, padx=10, pady=8, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)
        
        tk.Label(card, text=icon, font=("Arial", 30),
                fg='white', bg='#2a1f1a').pack(pady=(12, 4))
        
        tk.Label(card, text=title, font=("Arial", 11),
                fg='#888', bg='#2a1f1a').pack()
        
        tk.Label(card, text=value, font=("Arial", 18, "bold"),
                fg='white', bg='#2a1f1a').pack(pady=(4, 12))
    
    def create_emotion_pie_chart(self, parent):
        """Create emotion distribution pie chart"""
        chart_frame = tk.Frame(parent, bg='#2a1f1a', bd=2, relief="solid")
        chart_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        tk.Label(chart_frame, text="😊 Emotion Distribution",
                font=("Arial", 14, "bold"),
                fg='white', bg='#2a1f1a').pack(pady=8)
        
        if self.stats['emotions_count']:
            fig = Figure(figsize=(5, 4), facecolor='#2a1f1a')
            ax = fig.add_subplot(111)
            
            emotions = list(self.stats['emotions_count'].keys())
            counts = list(self.stats['emotions_count'].values())
            colors = [COLORS['emotions'].get(e.lower(), '#888') for e in emotions]
            
            ax.pie(counts, labels=emotions, colors=colors, autopct='%1.1f%%',
                  textprops={'color': 'white', 'fontsize': 10})
            ax.set_facecolor('#2a1f1a')
            
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
        else:
            tk.Label(chart_frame, text="No data available",
                    font=("Arial", 12), fg='#888', bg='#2a1f1a').pack(pady=50)
    
    def create_listening_time_chart(self, parent):
        """Create listening time bar chart"""
        chart_frame = tk.Frame(parent, bg='#2a1f1a', bd=2, relief="solid")
        chart_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        tk.Label(chart_frame, text="⏱️ Listening Time by Mood",
                font=("Arial", 14, "bold"),
                fg='white', bg='#2a1f1a').pack(pady=8)
        
        if self.stats['listening_time']:
            fig = Figure(figsize=(5, 4), facecolor='#2a1f1a')
            ax = fig.add_subplot(111)
            
            emotions = list(self.stats['listening_time'].keys())
            times = list(self.stats['listening_time'].values())
            colors = [COLORS['emotions'].get(e.lower(), '#888') for e in emotions]
            
            ax.bar(emotions, times, color=colors)
            ax.set_ylabel('Minutes', color='white')
            ax.set_facecolor('#2a1f1a')
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_color('white')
            
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
        else:
            tk.Label(chart_frame, text="No data available",
                    font=("Arial", 12), fg='#888', bg='#2a1f1a').pack(pady=50)
    
    def create_top_songs_section(self, parent):
        """Create top 10 songs list - FULL WIDTH"""
        section = tk.Frame(parent, bg='#2a1f1a', bd=2, relief="solid")
        section.pack(fill="x", padx=20, pady=8)  # Small padding from edges
        
        tk.Label(section, text="🎵 Top 10 Most Played Songs",
                font=("Arial", 14, "bold"),
                fg='white', bg='#2a1f1a').pack(pady=8)
        
        if self.stats['top_songs']:
            for idx, (song, count) in enumerate(self.stats['top_songs'], 1):
                song_frame = tk.Frame(section, bg='#1a0f0a')
                song_frame.pack(fill="x", padx=20, pady=5)
                
                tk.Label(song_frame, text=f"{idx}.",
                        font=("Arial", 12, "bold"),
                        fg=COLORS['primary'], bg='#1a0f0a',
                        width=3).pack(side="left")
                
                tk.Label(song_frame, text=song[:50],
                        font=("Arial", 11),
                        fg='white', bg='#1a0f0a').pack(side="left", padx=10)
                
                tk.Label(song_frame, text=f"▶️ {count}x",
                        font=("Arial", 10),
                        fg='#888', bg='#1a0f0a').pack(side="right")
        else:
            tk.Label(section, text="No songs played yet",
                    font=("Arial", 12), fg='#888', bg='#2a1f1a').pack(pady=30)
    
    def create_activity_charts(self, parent):
        """Create weekly and monthly activity charts"""
        charts_row = tk.Frame(parent, bg='#1a0f0a')
        charts_row.pack(fill="x", padx=20, pady=8)
        
        # Weekly activity
        weekly_frame = tk.Frame(charts_row, bg='#2a1f1a', bd=2, relief="solid")
        weekly_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        tk.Label(weekly_frame, text="📅 Weekly Activity",
                font=("Arial", 14, "bold"),
                fg='white', bg='#2a1f1a').pack(pady=6)
        
        fig = Figure(figsize=(5, 3), facecolor='#2a1f1a')
        ax = fig.add_subplot(111)
        
        days = ['Today', '1d', '2d', '3d', '4d', '5d', '6d']
        values = [self.stats['weekly_activity'][i] for i in range(7)]
        
        ax.plot(days, values, color=COLORS['primary'], marker='o', linewidth=2)
        ax.set_ylabel('Sessions', color='white')
        ax.set_facecolor('#2a1f1a')
        ax.tick_params(colors='white')
        ax.grid(color='#444', linestyle='--', linewidth=0.5)
        for spine in ax.spines.values():
            spine.set_color('white')
        
        canvas = FigureCanvasTkAgg(fig, weekly_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
    
    def create_accuracy_chart(self, parent):
        """Create accuracy over time chart - FULL WIDTH"""
        section = tk.Frame(parent, bg='#2a1f1a', bd=2, relief="solid")
        section.pack(fill="x", padx=20, pady=15)  # Small padding from edges
        
        tk.Label(section, text="🎯 Detection Accuracy Over Time",
                font=("Arial", 14, "bold"),
                fg='white', bg='#2a1f1a').pack(pady=6)
        
        if self.stats['accuracy']:
            fig = Figure(figsize=(10, 3), facecolor='#2a1f1a')
            ax = fig.add_subplot(111)
            
            sessions = list(range(1, len(self.stats['accuracy']) + 1))
            
            ax.plot(sessions, self.stats['accuracy'], color=COLORS['success'],
                   marker='o', markersize=3, linewidth=1.5)
            ax.axhline(y=70, color='yellow', linestyle='--', linewidth=1,
                      label='Target (70%)')
            ax.set_xlabel('Session Number', color='white')
            ax.set_ylabel('Accuracy (%)', color='white')
            ax.set_facecolor('#2a1f1a')
            ax.tick_params(colors='white')
            ax.grid(color='#444', linestyle='--', linewidth=0.5)
            ax.legend(facecolor='#2a1f1a', edgecolor='white', labelcolor='white')
            for spine in ax.spines.values():
                spine.set_color('white')
            
            canvas = FigureCanvasTkAgg(fig, section)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10, padx=10, fill="x")
    
    def load_background(self):
        """Load background image"""
        try:
            if os.path.exists('background.jpg'):
                img = Image.open('background.jpg')
            else:
                img = Image.new('RGB', (1920, 1080), '#0a0a0a')
            
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            
            if w <= 1:
                w = self.canvas.winfo_screenwidth()
            if h <= 1:
                h = self.canvas.winfo_screenheight()
            
            iw, ih = img.size
            scale = max(w / iw, h / ih)
            nw = int(iw * scale)
            nh = int(ih * scale)
            
            img = img.resize((nw, nh), Image.Resampling.LANCZOS)
            
            left = (nw - w) // 2
            top = (nh - h) // 2
            img = img.crop((left, top, left + w, top + h))
            
            img = img.filter(ImageFilter.GaussianBlur(radius=3))
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.6)
            
            bg_img = ImageTk.PhotoImage(img)
            self.canvas.create_image(w // 2, h // 2, image=bg_img, anchor='center')
            
            return bg_img
        except Exception as e:
            print(f"BG error: {e}")
            self.canvas.configure(bg='#0a0a0a')
            return None
    
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


if __name__ == "__main__":
    StatisticsPage()