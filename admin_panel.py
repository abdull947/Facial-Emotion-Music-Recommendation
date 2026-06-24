# admin_panel.py - FINAL VERSION - ALL ISSUES FIXED
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import hashlib
import shutil
import os
from datetime import datetime
from utils import *
from config import *

class AdminDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FEMR - Admin Panel")
        self.root.state('zoomed')
        self.root.configure(bg='black')
        
        self.create_ui()
        self.root.mainloop()
    
    def create_ui(self):
        # Canvas for background
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='#1a1a1a')
        self.canvas.pack(fill="both", expand=True)
        self.canvas.update()
        self.load_background()
        
        screen_width = self.canvas.winfo_width()
        screen_height = self.canvas.winfo_height()
        
        # Top bar
        top_bar = tk.Frame(self.canvas, bg='#1a0f0a', height=50)
        self.top_bar_win = self.canvas.create_window(
            screen_width // 2, 25,
            window=top_bar, width=screen_width, height=50
        )
        
        tk.Label(top_bar, text="👤 Admin", 
                font=("Arial", 12, "bold"),
                fg='white', bg='#1a0f0a').pack(side="left", padx=20, pady=12)
        
        tk.Button(top_bar, text="🚪 Logout", 
                 font=("Arial", 10, "bold"),
                 bg=COLORS['primary'], fg="white",
                 bd=0, cursor="hand2", padx=15, pady=6,
                 command=self.logout).pack(side="right", padx=20, pady=12)
        
        # DIRECT content on canvas - Position below top bar
        container_width = int(screen_width * 0.85)
        
        # Content starts at y=70 (below 50px top bar + 20px spacing)
        # Use dark semi-transparent color instead of empty string 0a0a0a
        content_frame = tk.Frame(self.canvas, bg='#1a0f0a') 
        self.content_win = self.canvas.create_window(
            screen_width // 2,
            screen_height // 2 + 40,  # Adjusted to account for top bar
            window=content_frame, anchor='center',
            width=container_width
        )
        
        # Window resize
        def update_pos(e=None):
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            self.canvas.coords(self.top_bar_win, w // 2, 25)
            self.canvas.itemconfig(self.top_bar_win, width=w)
            self.canvas.coords(self.content_win, w // 2, h // 2 + 40)
            self.canvas.itemconfig(self.content_win, width=int(w * 0.85))
        
        self.root.bind('<Configure>', update_pos)
        
        # Title - SMALLER
        tk.Label(content_frame, text="FEMR - Admin Panel", 
                font=("Arial", 24, "bold"),
                fg=COLORS['primary'], bg='#1a0f0a').pack(pady=12)
        
        # Sections
        self.create_user_section(content_frame)
        self.create_song_section(content_frame)
    
    def create_user_section(self, parent):
        # Add spacing at top - use dark color
        tk.Frame(parent, bg='#0a0a0a', height=5).pack()
        
        tk.Label(parent, text="👤 Users Management", 
                font=("Arial", 18, "bold"),
                fg='white', bg='#1a0f0a').pack(anchor="w", padx=30, pady=(5, 10))
        
        # FULL WIDTH table frame
        table_outer = tk.Frame(parent, bg='#1a0f0a')
        table_outer.pack(fill="both", expand=True, padx=30, pady=(0, 15))
        
        table_frame = tk.Frame(table_outer, bg='#dee2e6', bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True)
        
        # Header row
        header = tk.Frame(table_frame, bg='#17a2b8', height=50)
        header.pack(fill="both", expand=True)
        header.pack_propagate(False)
        
        # Grid layout for equal distribution
        header.grid_columnconfigure(0, weight=1, minsize=60)   # S.No
        header.grid_columnconfigure(1, weight=2, minsize=150)  # Name
        header.grid_columnconfigure(2, weight=3, minsize=220)  # Email (NEW)
        header.grid_columnconfigure(3, weight=2, minsize=120)  # Password
        header.grid_columnconfigure(4, weight=3, minsize=220)  # Actions00)
        
        tk.Label(header, text="S.No.", font=("Arial", 12, "bold"),
                fg='white', bg='#17a2b8', 
                bd=0).grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        
        tk.Label(header, text="Name", font=("Arial", 12, "bold"),
                fg='white', bg='#17a2b8', 
                bd=0).grid(row=0, column=1, sticky="nsew", padx=1, pady=1)
        
        tk.Label(header, text="Email", font=("Arial", 12, "bold"),
                fg='white', bg='#17a2b8', 
                bd=0).grid(row=0, column=2, sticky="nsew", padx=1, pady=1)
        
        tk.Label(header, text="Password", font=("Arial", 12, "bold"),
                fg='white', bg='#17a2b8', 
                bd=0).grid(row=0, column=3, sticky="nsew", padx=1, pady=1)
        
        tk.Label(header, text="Actions", font=("Arial", 12, "bold"),
                fg='white', bg='#17a2b8', 
                bd=0).grid(row=0, column=4, sticky="nsew", padx=1, pady=1)
        
        # Content container
        self.user_container = tk.Frame(table_frame, bg='white')
        self.user_container.pack(fill="both", expand=True)
        
        self.load_users()
    
    def create_song_section(self, parent):
        # Add spacing - use dark color
        tk.Frame(parent, bg='#1a0f0a', height=5).pack()
        
        # Header with Add button on RIGHT
        header_frame = tk.Frame(parent, bg='#1a0f0a')
        header_frame.pack(fill="x", padx=30, pady=(5, 10))
        
        tk.Label(header_frame, text="🎵 Songs Management", 
                font=("Arial", 18, "bold"),
                fg='white', bg='#1a0f0a').pack(side="left")
        
        # Add button on RIGHT side - SMALLER
        tk.Button(header_frame, text="➕ Add Song", 
                 font=("Arial", 10, "bold"),
                 bg=COLORS['primary'], fg="white",
                 bd=0, cursor="hand2", padx=5, pady=5,
                 command=self.add_new_song).pack(side="right")
        
        # FULL WIDTH table frame
        table_outer = tk.Frame(parent, bg='#1a0f0a')
        table_outer.pack(fill="both", expand=True, padx=30, pady=(0, 15))
        
        table_frame = tk.Frame(table_outer, bg='#dee2e6', bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True)
        
        # Header row
        header = tk.Frame(table_frame, bg='#17a2b8', height=50)
        header.pack(fill="both", expand=True)
        header.pack_propagate(False)
        
        # Grid layout for equal distribution
        header.grid_columnconfigure(0, weight=1, minsize=60)   # S.No
        header.grid_columnconfigure(1, weight=4, minsize=300)  # Song Name
        header.grid_columnconfigure(2, weight=3, minsize=200)  # Artist
        header.grid_columnconfigure(3, weight=1, minsize=100)  # Duration
        header.grid_columnconfigure(4, weight=1, minsize=100)  # Emotion
        header.grid_columnconfigure(5, weight=1, minsize=100)  # Actions
        
        tk.Label(header, text="S.No.", font=("Arial", 12, "bold"),
                fg='white', bg='#17a2b8', 
                bd=0).grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        
        tk.Label(header, text="Song Name", font=("Arial", 12, "bold"),
                fg='white', bg='#17a2b8', 
                bd=0).grid(row=0, column=1, sticky="nsew", padx=1, pady=1)
        
        tk.Label(header, text="Artist", font=("Arial", 12, "bold"),
                fg='white', bg='#17a2b8', 
                bd=0).grid(row=0, column=2, sticky="nsew", padx=1, pady=1)
        
        tk.Label(header, text="Duration", font=("Arial", 12, "bold"),
                fg='white', bg='#17a2b8', 
                bd=0).grid(row=0, column=3, sticky="nsew", padx=1, pady=1)
        
        tk.Label(header, text="Emotion", font=("Arial", 12, "bold"),
                fg='white', bg='#17a2b8', 
                bd=0).grid(row=0, column=4, sticky="nsew", padx=1, pady=1)
        
        tk.Label(header, text="Actions", font=("Arial", 12, "bold"),
                fg='white', bg='#17a2b8', 
                bd=0).grid(row=0, column=5, sticky="nsew", padx=1, pady=1)
        
        # SCROLLABLE content - INCREASED HEIGHT to 280px
        content_frame = tk.Frame(table_frame, bg='white', height=280)
        content_frame.pack(fill="both", expand=True)
        content_frame.pack_propagate(False)
        
        content_canvas = tk.Canvas(content_frame, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", 
                                command=content_canvas.yview, width=10)
        
        self.song_container = tk.Frame(content_canvas, bg='white')
        
        # Bind width to canvas width
        def configure_width(e):
            content_canvas.configure(scrollregion=content_canvas.bbox("all"))
        
        canvas_window = content_canvas.create_window((0, 0), window=self.song_container, anchor="nw")
        self.song_container.bind("<Configure>", configure_width)
        
        # Update canvas window width when canvas resizes
        def on_canvas_configure(e):
            content_canvas.itemconfig(canvas_window, width=e.width)
        content_canvas.bind("<Configure>", on_canvas_configure)
        
        content_canvas.configure(yscrollcommand=scrollbar.set)
        
        content_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel
        def song_wheel(event):
            content_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        content_canvas.bind("<Enter>", lambda e: self.root.bind("<MouseWheel>", song_wheel))
        content_canvas.bind("<Leave>", lambda e: self.root.unbind_all("<MouseWheel>"))
        
        self.load_songs()
        
        # Bottom spacing
        tk.Frame(parent, bg='#0a0a0a', height=10).pack()
    
    def load_users(self):
        for widget in self.user_container.winfo_children():
            widget.destroy()
        
        users = list(users_collection.find({}))
        
        if not users:
            tk.Label(self.user_container, text="No users found", 
                    font=("Arial", 12), fg='#888', bg='white').pack(pady=50)
            return
        
        for idx, user in enumerate(users, 1):
            self.create_user_row(idx, user)
    
    def create_user_row(self, idx, user):
        username = user.get('username', 'Unknown')
        email = user.get('email', 'N/A')  # Get email from user document
        
        # Alternating row colors
        bg_color = '#f8f9fa' if idx % 2 == 0 else 'white'
        
        # TALLER row - increased to 80px
        row = tk.Frame(self.user_container, bg=bg_color, height=80)
        row.pack(fill="both", expand=True)
        row.pack_propagate(False)
        
        # Grid layout matching header - NOW 5 COLUMNS
        row.grid_columnconfigure(0, weight=1, minsize=60)   # S.No
        row.grid_columnconfigure(1, weight=2, minsize=150)  # Name
        row.grid_columnconfigure(2, weight=3, minsize=220)  # Email (NEW)
        row.grid_columnconfigure(3, weight=2, minsize=120)  # Password
        row.grid_columnconfigure(4, weight=3, minsize=220)  # Actions
        
        # S.No. - with border
        tk.Label(row, text=str(idx), font=("Arial", 11),
                fg='#333', bg=bg_color,
                bd=0, highlightthickness=1, highlightbackground='#dee2e6').grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        
        # Name - with border
        tk.Label(row, text=username, font=("Arial", 11, "bold"),
                fg='#333', bg=bg_color,
                bd=0, highlightthickness=1, highlightbackground='#dee2e6').grid(row=0, column=1, sticky="nsew", padx=1, pady=1)
        
        # Email - with border (NEW COLUMN)
        tk.Label(row, text=email, font=("Arial", 10),
                fg='#555', bg=bg_color,
                bd=0, highlightthickness=1, highlightbackground='#dee2e6').grid(row=0, column=2, sticky="nsew", padx=1, pady=1)
        
        # Password - with border (NOW COLUMN 3)
        tk.Label(row, text="••••••••", font=("Arial", 10),
                fg='#666', bg=bg_color,
                bd=0, highlightthickness=1, highlightbackground='#dee2e6').grid(row=0, column=3, sticky="nsew", padx=1, pady=1)
        
        # Actions - with border (NOW COLUMN 4)
        actions_cell = tk.Frame(row, bg=bg_color, highlightthickness=1, highlightbackground='#dee2e6')
        actions_cell.grid(row=0, column=4, sticky="nsew", padx=1, pady=1)
        
        # Center container
        center_container = tk.Frame(actions_cell, bg=bg_color)
        center_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # View History - Badge with VERTICAL PADDING
        view_btn = tk.Label(center_container, text="📜 View", 
                 font=("Arial", 9, "bold"),
                 bg='#6c757d', fg="white",
                 padx=10, pady=6, cursor="hand2")  # Added vertical padding
        view_btn.pack(side="left", padx=3, pady=8)  # Vertical spacing from cell
        view_btn.bind("<Button-1>", lambda e: self.view_history(username))
        
        # Update - Badge with VERTICAL PADDING
        update_btn = tk.Label(center_container, text="✏️ Update", 
                 font=("Arial", 9, "bold"),
                 bg='#17a2b8', fg="white",
                 padx=10, pady=6, cursor="hand2")
        update_btn.pack(side="left", padx=3, pady=8)
        update_btn.bind("<Button-1>", lambda e: self.update_user(username))
        
        # Delete - Badge with VERTICAL PADDING
        delete_btn = tk.Label(center_container, text="🗑️ Delete", 
                 font=("Arial", 9, "bold"),
                 bg='#dc3545', fg="white",
                 padx=10, pady=6, cursor="hand2")
        delete_btn.pack(side="left", padx=3, pady=8)
        delete_btn.bind("<Button-1>", lambda e: self.delete_user(username))
    
    def load_songs(self):
        for widget in self.song_container.winfo_children():
            widget.destroy()
        
        cache_doc = cache_collection.find_one({'_id': 'music_cache'})
        if not cache_doc:
            tk.Label(self.song_container, text="No songs in cache", 
                    font=("Arial", 12), fg='#888', bg='white').pack(pady=50)
            return
        
        cache_data = cache_doc.get('data', {})
        idx = 1
        for emotion, data in cache_data.items():
            for song in data.get('songs', []):
                if os.path.exists(get_cache_path(song['id'])):
                    self.create_song_row(idx, song, emotion)
                    idx += 1
    
    def create_song_row(self, idx, song, emotion):
        # Alternating row colors
        bg_color = '#f8f9fa' if idx % 2 == 0 else 'white'
        
        # TALLER row - increased to 65px
        row = tk.Frame(self.song_container, bg=bg_color, height=65)
        row.pack(fill="both", expand=True)
        row.pack_propagate(False)
        
        emotion_color = COLORS['emotions'].get(emotion.lower(), COLORS['primary'])
        
        # Grid layout matching header
        row.grid_columnconfigure(0, weight=1, minsize=60)
        row.grid_columnconfigure(1, weight=4, minsize=300)
        row.grid_columnconfigure(2, weight=3, minsize=200)
        row.grid_columnconfigure(3, weight=1, minsize=100)
        row.grid_columnconfigure(4, weight=1, minsize=100)
        row.grid_columnconfigure(5, weight=1, minsize=100)
        
        # S.No. - with border
        tk.Label(row, text=str(idx), font=("Arial", 11),
                fg='#333', bg=bg_color,
                bd=0, highlightthickness=1, highlightbackground='#dee2e6').grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        
        # Song Name - with border
        tk.Label(row, text=song['title'][:50], font=("Arial", 10),
                fg='#333', bg=bg_color, anchor="w", padx=10,
                bd=0, highlightthickness=1, highlightbackground='#dee2e6').grid(row=0, column=1, sticky="nsew", padx=1, pady=1)
        
        # Artist - with border
        tk.Label(row, text=song['artist'][:30], font=("Arial", 10),
                fg='#555', bg=bg_color, anchor="w", padx=10,
                bd=0, highlightthickness=1, highlightbackground='#dee2e6').grid(row=0, column=2, sticky="nsew", padx=1, pady=1)
        
        # Duration - with border
        tk.Label(row, text=song['duration_str'], font=("Arial", 10),
                fg='#666', bg=bg_color,
                bd=0, highlightthickness=1, highlightbackground='#dee2e6').grid(row=0, column=3, sticky="nsew", padx=1, pady=1)
        
        # Emotion - with border and PADDED badge
        emotion_cell = tk.Frame(row, bg=bg_color, highlightthickness=1, highlightbackground='#dee2e6')
        emotion_cell.grid(row=0, column=4, sticky="nsew", padx=1, pady=1)
        
        # Center container for emotion badge
        emotion_center = tk.Frame(emotion_cell, bg=bg_color)
        emotion_center.place(relx=0.5, rely=0.5, anchor="center")
        
        emotion_badge = tk.Label(emotion_center, text=emotion.upper(), 
                                font=("Arial", 9, "bold"),
                                fg='white', bg=emotion_color, 
                                padx=8, pady=5)
        emotion_badge.pack(pady=6)  # Vertical spacing from cell edges
        
        # Actions - with border and PADDED badge
        actions_cell = tk.Frame(row, bg=bg_color, highlightthickness=1, highlightbackground='#dee2e6')
        actions_cell.grid(row=0, column=5, sticky="nsew", padx=1, pady=1)
        
        # Center the delete badge
        center = tk.Frame(actions_cell, bg=bg_color)
        center.place(relx=0.5, rely=0.5, anchor="center")
        
        delete_btn = tk.Label(center, text="🗑️ Delete", 
                 font=("Arial", 9, "bold"),
                 bg='#dc3545', fg="white",
                 padx=8, pady=5, cursor="hand2")
        delete_btn.pack(pady=6)  # Vertical spacing from cell edges
        delete_btn.bind("<Button-1>", lambda e: self.delete_song(song['id'], emotion))
    
    def view_history(self, username):
        win = tk.Toplevel(self.root)
        win.title(f"{username}'s History")
        win.geometry("850x650")
        win.configure(bg='#1a0f0a')
        
        x = (win.winfo_screenwidth() // 2) - 425
        y = (win.winfo_screenheight() // 2) - 325
        win.geometry(f"850x650+{x}+{y}")
        
        # Header
        header = tk.Frame(win, bg='#2a1f1a', height=70)
        header.pack(fill="x")
        
        tk.Label(header, text=f"📜 {username}'s History", 
                font=("Arial", 20, "bold"),
                fg='white', bg='#2a1f1a').pack(side="left", padx=25, pady=20)
        
        tk.Button(header, text="🗑️ Clear All", 
                 font=("Arial", 10, "bold"),
                 bg=COLORS['primary'], fg="white",
                 bd=0, cursor="hand2", padx=15, pady=8,
                 command=lambda: self.clear_history(username, win)).pack(side="right", padx=25)
        
        tk.Button(header, text="✖ Close", 
                 font=("Arial", 10, "bold"),
                 bg='#3a2510', fg="white",
                 bd=0, cursor="hand2", padx=15, pady=8,
                 command=win.destroy).pack(side="right", padx=10)
        
        # SCROLLABLE
        canvas = tk.Canvas(win, bg='#1a0f0a', highlightthickness=0)
        scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview, width=12)
        scrollable = tk.Frame(canvas, bg='#1a0f0a')
        
        scrollable.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y", pady=20)
        
        # Mouse wheel
        def hist_wheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        win.bind("<MouseWheel>", hist_wheel)
        
        history = load_history(username)
        if not history:
            tk.Label(scrollable, text="No history", 
                    font=("Arial", 14), fg='#888', bg='#1a0f0a').pack(pady=150)
        else:
            for entry in history:
                self.create_history_card(scrollable, entry)
    
    def create_history_card(self, parent, entry):
        card = tk.Frame(parent, bg='#2a1f1a')
        card.pack(fill="x", pady=8, padx=10)
        
        emotion_color = COLORS['emotions'].get(entry['emotion'].lower(), COLORS['primary'])
        tk.Frame(card, bg=emotion_color, height=4).pack(fill="x")
        
        content = tk.Frame(card, bg='#2a1f1a')
        content.pack(fill="x", padx=20, pady=15)
        
        header = tk.Frame(content, bg='#2a1f1a')
        header.pack(fill="x", pady=(0, 10))
        
        tk.Label(header, text=f"😊 {entry['emotion'].upper()}", 
                font=("Arial", 15, "bold"),
                fg=emotion_color, bg='#2a1f1a').pack(side="left")
        
        tk.Label(header, text=f"{entry['confidence']:.0%}", 
                font=("Arial", 12), fg='#bbb', bg='#2a1f1a').pack(side="left", padx=15)
        
        tk.Label(header, text=entry['date_formatted'], 
                font=("Arial", 10), fg='#888', bg='#2a1f1a').pack(side="right")
        
        tk.Label(content, text=f"🎵 {len(entry['songs'])} songs", 
                font=("Arial", 11, "bold"), fg='white', bg='#2a1f1a').pack(anchor="w", pady=(0, 5))
        
        for i, song in enumerate(entry['songs'][:5], 1):
            tk.Label(content, text=f"  {i}. {song['title'][:60]}", 
                    font=("Arial", 9), fg='#ddd', bg='#2a1f1a').pack(anchor="w", pady=1)
        
        if len(entry['songs']) > 5:
            tk.Label(content, text=f"  ... +{len(entry['songs']) - 5} more", 
                    font=("Arial", 9, "italic"), fg='#888', bg='#2a1f1a').pack(anchor="w")
    
    def clear_history(self, username, win):
        if messagebox.askyesno("Confirm", f"Clear history for {username}?"):
            clear_history(username)
            messagebox.showinfo("Success", "History cleared!")
            win.destroy()
    
    def update_user(self, username):
        win = tk.Toplevel(self.root)
        win.title(f"Update {username}")
        win.geometry("450x350")
        win.configure(bg='#1a0f0a')
        
        x = (win.winfo_screenwidth() // 2) - 225
        y = (win.winfo_screenheight() // 2) - 175
        win.geometry(f"450x350+{x}+{y}")
        
        tk.Label(win, text="✏️ Update User", 
                font=("Arial", 20, "bold"),
                fg=COLORS['primary'], bg='#1a0f0a').pack(pady=25)
        
        form = tk.Frame(win, bg='#1a0f0a')
        form.pack(padx=40, fill="x")
        
        tk.Label(form, text="Username (read-only)", 
                font=("Arial", 10, "bold"),
                fg='white', bg='#1a0f0a').pack(anchor="w", pady=(10, 5))
        
        user_entry = tk.Entry(form, font=("Arial", 12),
                             bg='#2a1f1a', fg='#888',
                             state='readonly', relief="flat", bd=10)
        user_entry.insert(0, username)
        user_entry.pack(fill="x")
        
        tk.Label(form, text="New Password", 
                font=("Arial", 10, "bold"),
                fg='white', bg='#1a0f0a').pack(anchor="w", pady=(20, 5))
        
        pass_entry = tk.Entry(form, font=("Arial", 12),
                             bg='#2a1f1a', fg='white',
                             insertbackground='white',
                             relief="flat", bd=10)
        pass_entry.pack(fill="x")
        
        def update():
            pwd = pass_entry.get().strip()
            if not pwd or len(pwd) < 6:
                messagebox.showerror("Error", "Password must be 6+ characters!")
                return
            
            users_collection.update_one(
                {'username': username},
                {'$set': {'password': hashlib.sha256(pwd.encode()).hexdigest()}}
            )
            messagebox.showinfo("Success", "Password updated!")
            win.destroy()
            self.load_users()
        
        tk.Button(form, text="✔ Update Password", 
                 font=("Arial", 13, "bold"),
                 bg=COLORS['primary'], fg="white",
                 bd=0, cursor="hand2", height=2,
                 command=update).pack(fill="x", pady=30)
    
    def delete_user(self, username):
        if username == "Admin":
            messagebox.showerror("Error", "Cannot delete admin!")
            return
        
        if messagebox.askyesno("Confirm", f"Delete '{username}' and all data?"):
            users_collection.delete_one({'username': username})
            history_collection.delete_many({'user': username})
            favorites_collection.delete_one({'username': username})
            messagebox.showinfo("Success", f"'{username}' deleted!")
            self.load_users()
    
    def delete_song(self, video_id, emotion):
        if messagebox.askyesno("Confirm", "Delete this song?"):
            cache_doc = cache_collection.find_one({'_id': 'music_cache'})
            if cache_doc:
                cache_data = cache_doc.get('data', {})
                if emotion in cache_data:
                    cache_data[emotion]['songs'] = [s for s in cache_data[emotion]['songs'] if s['id'] != video_id]
                    cache_collection.update_one({'_id': 'music_cache'}, {'$set': {'data': cache_data}})
            
            audio_path = get_cache_path(video_id)
            if os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except:
                    pass
            
            messagebox.showinfo("Success", "Song deleted!")
            self.load_songs()
    
    def add_new_song(self):
        win = tk.Toplevel(self.root)
        win.title("Add New Song")
        win.geometry("500x600")
        win.configure(bg='#1a0f0a')
        
        x = (win.winfo_screenwidth() // 2) - 250
        y = (win.winfo_screenheight() // 2) - 300
        win.geometry(f"500x600+{x}+{y}")
        
        tk.Label(win, text="➕ Add New Song", 
                font=("Arial", 22, "bold"),
                fg=COLORS['primary'], bg='#1a0f0a').pack(pady=25)
        
        form = tk.Frame(win, bg='#1a0f0a')
        form.pack(padx=40, fill="both", expand=True)
        
        audio_path = tk.StringVar()
        
        tk.Label(form, text="Choose Song File", 
                font=("Arial", 11, "bold"),
                fg='white', bg='#1a0f0a').pack(anchor="w", pady=(10, 5))
        
        audio_frame = tk.Frame(form, bg='white', bd=2, relief="solid")
        audio_frame.pack(fill="x")
        
        audio_inner = tk.Frame(audio_frame, bg='white')
        audio_inner.pack(fill="x", padx=8, pady=10)  # Increased padding for height
        
        audio_entry = tk.Entry(audio_inner, textvariable=audio_path,
                              font=("Arial", 10), bg='white', fg='black',
                              state='readonly', relief="flat", bd=0)
        audio_entry.pack(side="left", fill="x", expand=True)
        
        tk.Button(audio_inner, text="📁 Browse", 
                 font=("Arial", 9, "bold"),
                 bg='#3a2510', fg="white", bd=0, cursor="hand2",
                 command=lambda: audio_path.set(filedialog.askopenfilename(
                     filetypes=[("Audio", "*.mp3 *.wav *.m4a")]))).pack(side="right")
        
        # TALLER input fields
        tk.Label(form, text="Song Title", 
                font=("Arial", 11, "bold"),
                fg='white', bg='#1a0f0a').pack(anchor="w", pady=(15, 5))
        
        title_entry = tk.Entry(form, font=("Arial", 13),  # Bigger font
                              bg='white', fg='black',
                              insertbackground='black',
                              relief="solid", bd=2)
        title_entry.pack(fill="x", ipady=5)  # ipady for height
        
        tk.Label(form, text="Artist Name", 
                font=("Arial", 11, "bold"),
                fg='white', bg='#1a0f0a').pack(anchor="w", pady=(15, 5))
        
        artist_entry = tk.Entry(form, font=("Arial", 13),
                               bg='white', fg='black',
                               insertbackground='black',
                               relief="solid", bd=2)
        artist_entry.pack(fill="x", ipady=5)
        
        tk.Label(form, text="Duration (e.g., 3:45)", 
                font=("Arial", 11, "bold"),
                fg='white', bg='#1a0f0a').pack(anchor="w", pady=(15, 5))
        
        duration_entry = tk.Entry(form, font=("Arial", 13),
                                 bg='white', fg='black',
                                 insertbackground='black',
                                 relief="solid", bd=2)
        duration_entry.pack(fill="x", ipady=5)
        
        tk.Label(form, text="Select Emotion", 
                font=("Arial", 11, "bold"),
                fg='white', bg='#1a0f0a').pack(anchor="w", pady=(15, 5))
        
        emotions = ["happy", "sad", "angry", "fear", "disgust", "surprise", "neutral"]
        emotion_var = tk.StringVar(value="happy")
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.TCombobox", 
                       fieldbackground='white',
                       background='white',
                       foreground='black',
                       arrowcolor='black',
                       borderwidth=2,
                       padding=8)  # Increased padding
        style.map('Custom.TCombobox',
                 fieldbackground=[('readonly', 'white')],
                 foreground=[('readonly', 'black')])
        
        emotion_dropdown = ttk.Combobox(form, textvariable=emotion_var,
                                       values=emotions, state='readonly',
                                       style="Custom.TCombobox",
                                       font=("Arial", 13), height=15)  # Taller dropdown
        emotion_dropdown.pack(fill="x")
        
        def submit():
            audio = audio_path.get()
            title = title_entry.get().strip()
            artist = artist_entry.get().strip()
            duration_str = duration_entry.get().strip()
            emotion = emotion_var.get()
            
            if not all([audio, title, artist, duration_str]):
                messagebox.showerror("Error", "Fill all fields!")
                return
            
            import time
            video_id = f"custom_{int(time.time())}"
            
            try:
                shutil.copy(audio, get_cache_path(video_id))
            except Exception as e:
                messagebox.showerror("Error", f"Copy failed: {e}")
                return
            
            new_song = {
                'id': video_id,
                'title': title,
                'artist': artist,
                'duration': parse_duration(duration_str),
                'duration_str': duration_str
            }
            
            cache_doc = cache_collection.find_one({'_id': 'music_cache'}) or {'_id': 'music_cache', 'data': {}}
            cache_data = cache_doc.get('data', {})
            
            if emotion not in cache_data:
                cache_data[emotion] = {
                    'songs': [],
                    'last_fetched': datetime.now(),
                    'last_used': datetime.now(),
                    'query': 'Admin upload'
                }
            
            cache_data[emotion]['songs'].append(new_song)
            cache_collection.update_one({'_id': 'music_cache'}, {'$set': {'data': cache_data}}, upsert=True)
            
            messagebox.showinfo("Success", "Song added!")
            win.destroy()
            self.load_songs()
        
        # CENTERED button with REDUCED width
        btn_container = tk.Frame(form, bg='#1a0f0a')
        btn_container.pack(pady=30)
        
        tk.Button(btn_container, text="✔ Add Song", 
                 font=("Arial", 13, "bold"),
                 bg=COLORS['primary'], fg="white",
                 bd=0, cursor="hand2", 
                 width=20,  # Fixed width instead of fill
                 padx=30, pady=12,
                 command=submit).pack()
    
    def load_background(self):
        try:
            if os.path.exists('background.jpg'):
                img = Image.open('background.jpg')
            else:
                img = self.create_gradient_bg()
            
            w = self.canvas.winfo_width() or self.canvas.winfo_screenwidth()
            h = self.canvas.winfo_height() or self.canvas.winfo_screenheight()
            
            iw, ih = img.size
            scale = max(w / iw, h / ih)
            img = img.resize((int(iw * scale), int(ih * scale)), Image.Resampling.LANCZOS)
            
            left = (img.width - w) // 2
            top = (img.height - h) // 2
            img = img.crop((left, top, left + w, top + h))
            
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
            img = ImageEnhance.Brightness(img).enhance(0.75)
            
            self.bg_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(w // 2, h // 2, image=self.bg_image, anchor='center')
        except Exception as e:
            print(f"BG error: {e}")
            self.canvas.configure(bg='#0a0a0a')
    
    def create_gradient_bg(self):
        from PIL import ImageDraw
        import random
        img = Image.new('RGB', (1920, 1080), '#0a0a0a')
        draw = ImageDraw.Draw(img)
        for _ in range(30):
            x, y = random.randint(0, 1920), random.randint(0, 1080)
            size = random.randint(100, 300)
            color = random.choice(['#ff6b35', '#f7931e', '#fdc830', '#c471f5', '#E74C3C'])
            draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
        return img.filter(ImageFilter.GaussianBlur(radius=120))
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure?"):
            self.root.destroy()
            from main import main
            main()