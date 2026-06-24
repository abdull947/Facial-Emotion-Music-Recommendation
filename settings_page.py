"""
settings_page.py - User Settings & Profile Page (FIXED VERSION)
Features: Profile picture, Change password, Email preferences, Notifications, Theme
FIXES: Full-width cards, proper scrolling with mouse wheel
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageDraw
import hashlib
import shutil
import os
from datetime import datetime
from utils import *
from config import *

class SettingsPage:
    def __init__(self, parent_callback=None):
        self.root = tk.Tk()
        self.root.title("EmoTune - Settings")
        
        # CRITICAL: Hide window immediately
        self.root.withdraw()
        
        self.root.state('zoomed')
        self.root.configure(bg='black')
        
        self.parent_callback = parent_callback
        self.current_user = get_current_user()
        
        # Load user data
        self.user_data = users_collection.find_one({'username': self.current_user})
        self.settings = self.load_user_settings()
        
        self.root.update_idletasks()
        self.create_ui()
        
        # CRITICAL: Show window only after complete
        self.root.deiconify()
        
        self.root.mainloop()
    
    def load_user_settings(self):
        """Load user settings from database"""
        settings = settings_collection.find_one({'username': self.current_user})
        if settings:
            return settings
        else:
            # Create default settings
            default = DEFAULT_SETTINGS.copy()
            default['username'] = self.current_user
            default['created_at'] = datetime.now()
            settings_collection.insert_one(default)
            return default
    
    def save_settings(self):
        """Save settings to database"""
        self.settings['updated_at'] = datetime.now()
        settings_collection.update_one(
            {'username': self.current_user},
            {'$set': self.settings},
            upsert=True
        )
    
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
        
        tk.Label(top_bar, text="⚙️ Settings", 
                font=("Arial", 16, "bold"),
                fg=COLORS['primary'], bg='#1a0f0a').pack(side="left", expand=True)
        
        # Get screen dimensions
        screen_width = self.canvas.winfo_width()
        screen_height = self.canvas.winfo_height()

        # LEFT POSITION - 35% from left (like HistoryViewer)
        left_x = int(screen_width * 0.35)
        center_y = screen_height // 2 + 20
        
        # FIXED WIDTH - 700 pixels (same as HistoryViewer)
        self.container_width = 700
        available_height = screen_height - 80
        
        # Main container frame
        main_container = tk.Frame(self.canvas, bg='#1a0f0a', 
                                 width=self.container_width, 
                                 height=available_height,
                                 highlightthickness=1,
                                 highlightbackground='#3a2510')
        
        self.container_win = self.canvas.create_window(
            left_x,  # LEFT position instead of center
            center_y,
            window=main_container, 
            anchor='center'
        )
        
        # CRITICAL: Prevent frame from resizing
        main_container.pack_propagate(False)
        main_container.grid_propagate(False)
        
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
        
        # Frame that holds all settings sections
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
        
        scroll_canvas.bind("<Enter>", lambda e: scroll_canvas.bind_all("<MouseWheel>", on_mousewheel))
        scroll_canvas.bind("<Leave>", lambda e: scroll_canvas.unbind_all("<MouseWheel>"))
        
        # Profile Section
        self.create_profile_section(scrollable_frame)
        
        # Security Section
        self.create_security_section(scrollable_frame)
        
        # Preferences Section
        self.create_preferences_section(scrollable_frame)
        
        # Save Button - FULL WIDTH
        save_btn_container = tk.Frame(scrollable_frame, bg='#1a0f0a')
        save_btn_container.pack(fill="x", pady=30)
        
        tk.Button(save_btn_container, text="💾 Save All Changes",
                 font=("Arial", 14, "bold"),
                 bg=COLORS['success'], fg="white",
                 bd=0, cursor="hand2", pady=12,
                 activebackground='#27AE60',
                 command=self.save_all_changes).pack(fill="x", padx=10)
        
        # Resize handler
        def update_pos(e=None):
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            
            # Maintain left position at 35%
            lx = int(w * 0.35)
            cy = h // 2 + 20
            avail_h = h - 80
            
            self.canvas.coords(self.top_bar_win, w // 2, 25)
            self.canvas.itemconfig(self.top_bar_win, width=w)
            
            # Update to left position
            self.canvas.coords(self.container_win, lx, cy)
            main_container.config(height=avail_h)
        
        self.root.bind('<Configure>', update_pos)
    
    def create_profile_section(self, parent):
        """Profile Picture Section - FULL WIDTH"""
        section = tk.Frame(parent, bg='#2a1f1a', bd=2, relief="solid")
        section.pack(fill="x", padx=10, pady=10)  # Reduced padding to 10px
        
        tk.Label(section, text="👤 Profile", 
                font=("Arial", 16, "bold"),
                fg='white', bg='#2a1f1a').pack(anchor="w", padx=20, pady=10)
        
        # Profile picture container
        pic_container = tk.Frame(section, bg='#2a1f1a')
        pic_container.pack(pady=10)
        
        # Load and display profile picture
        self.profile_pic_label = tk.Label(pic_container, bg='#2a1f1a')
        self.profile_pic_label.pack()
        self.load_profile_picture()
        
        # Upload button
        tk.Button(pic_container, text="📸 Change Profile Picture",
                 font=("Arial", 11, "bold"),
                 bg=COLORS['primary'], fg="white",
                 bd=0, cursor="hand2", padx=20, pady=8,
                 activebackground=COLORS['primary_dark'],
                 command=self.upload_profile_picture).pack(pady=10)
        
        # User info
        info_frame = tk.Frame(section, bg='#2a1f1a')
        info_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(info_frame, text=f"Username: {self.current_user}",
                font=("Arial", 12),
                fg='white', bg='#2a1f1a').pack(anchor="w", pady=5)
        
        tk.Label(info_frame, text=f"Email: {self.user_data.get('email', 'Not set')}",
                font=("Arial", 12),
                fg='white', bg='#2a1f1a').pack(anchor="w", pady=5)
        
        member_since = self.user_data.get('created_at', datetime.now())
        if isinstance(member_since, datetime):
            member_text = member_since.strftime("%B %d, %Y")
        else:
            member_text = "Unknown"
        
        tk.Label(info_frame, text=f"Member since: {member_text}",
                font=("Arial", 12),
                fg='#888', bg='#2a1f1a').pack(anchor="w", pady=5)
    
    def create_security_section(self, parent):
        """Password Change Section - FULL WIDTH WITH EYE ICONS"""
        section = tk.Frame(parent, bg='#2a1f1a', bd=2, relief="solid")
        section.pack(fill="x", padx=10, pady=10)
        
        tk.Label(section, text="🔒 Security", 
                font=("Arial", 16, "bold"),
                fg='white', bg='#2a1f1a').pack(anchor="w", padx=20, pady=10)
        
        # Current password with eye icon
        tk.Label(section, text="Current Password:",
                font=("Arial", 11),
                fg='white', bg='#2a1f1a').pack(anchor="w", padx=20, pady=(10, 5))
        
        current_pwd_container = tk.Frame(section, bg='#1a0f0a')
        current_pwd_container.pack(fill="x", padx=20, pady=(0, 10))
        
        self.current_password_entry = tk.Entry(current_pwd_container, font=("Arial", 12),
                                               bg='#1a0f0a', fg='white',
                                               show='•', relief="flat", bd=10,
                                               insertbackground='white')
        self.current_password_entry.pack(side="left", fill="both", expand=True)
        
        self.current_pwd_visible = False
        self.current_pwd_toggle = tk.Button(current_pwd_container, text="👁", 
                                           font=("Arial", 14),
                                           fg='white', bg='#1a0f0a',
                                           bd=0, cursor="hand2",
                                           activebackground='#2a1510',
                                           width=3,
                                           command=lambda: self.toggle_password_visibility(
                                               self.current_password_entry,
                                               'current'))
        self.current_pwd_toggle.pack(side="right")
        
        # New password with eye icon
        tk.Label(section, text="New Password:",
                font=("Arial", 11),
                fg='white', bg='#2a1f1a').pack(anchor="w", padx=20, pady=(10, 5))
        
        new_pwd_container = tk.Frame(section, bg='#1a0f0a')
        new_pwd_container.pack(fill="x", padx=20, pady=(0, 10))
        
        self.new_password_entry = tk.Entry(new_pwd_container, font=("Arial", 12),
                                           bg='#1a0f0a', fg='white',
                                           show='•', relief="flat", bd=10,
                                           insertbackground='white')
        self.new_password_entry.pack(side="left", fill="both", expand=True)
        
        self.new_pwd_visible = False
        self.new_pwd_toggle = tk.Button(new_pwd_container, text="👁", 
                                        font=("Arial", 14),
                                        fg='white', bg='#1a0f0a',
                                        bd=0, cursor="hand2",
                                        activebackground='#2a1510',
                                        width=3,
                                        command=lambda: self.toggle_password_visibility(
                                            self.new_password_entry,
                                            'new'))
        self.new_pwd_toggle.pack(side="right")
        
        # Confirm password with eye icon
        tk.Label(section, text="Confirm New Password:",
                font=("Arial", 11),
                fg='white', bg='#2a1f1a').pack(anchor="w", padx=20, pady=(10, 5))
        
        confirm_pwd_container = tk.Frame(section, bg='#1a0f0a')
        confirm_pwd_container.pack(fill="x", padx=20, pady=(0, 10))
        
        self.confirm_password_entry = tk.Entry(confirm_pwd_container, font=("Arial", 12),
                                               bg='#1a0f0a', fg='white',
                                               show='•', relief="flat", bd=10,
                                               insertbackground='white')
        self.confirm_password_entry.pack(side="left", fill="both", expand=True)
        
        self.confirm_pwd_visible = False
        self.confirm_pwd_toggle = tk.Button(confirm_pwd_container, text="👁", 
                                           font=("Arial", 14),
                                           fg='white', bg='#1a0f0a',
                                           bd=0, cursor="hand2",
                                           activebackground='#2a1510',
                                           width=3,
                                           command=lambda: self.toggle_password_visibility(
                                               self.confirm_password_entry,
                                               'confirm'))
        self.confirm_pwd_toggle.pack(side="right")
        
        tk.Button(section, text="🔐 Change Password",
                 font=("Arial", 11, "bold"),
                 bg='#FF6B35', fg="white",
                 bd=0, cursor="hand2", padx=20, pady=8,
                 activebackground='#E85A25',
                 command=self.change_password).pack(pady=15)
    
    def create_preferences_section(self, parent):
        """Email & Notification Preferences - FULL WIDTH"""
        section = tk.Frame(parent, bg='#2a1f1a', bd=2, relief="solid")
        section.pack(fill="x", padx=10, pady=10)  # Reduced padding to 10px
        
        tk.Label(section, text="🔔 Preferences", 
                font=("Arial", 16, "bold"),
                fg='white', bg='#2a1f1a').pack(anchor="w", padx=20, pady=10)
        
        
        # Auto-play
        self.autoplay_var = tk.BooleanVar(value=self.settings.get('auto_play', True))
        autoplay_check = tk.Checkbutton(section, text="▶️ Auto-play music after detection",
                                       font=("Arial", 12),
                                       fg='white', bg='#2a1f1a',
                                       selectcolor='#1a0f0a',
                                       activebackground='#2a1f1a',
                                       activeforeground='white',
                                       variable=self.autoplay_var,
                                       command=lambda: self.settings.update({'auto_play': self.autoplay_var.get()}))
        autoplay_check.pack(anchor="w", padx=20, pady=10)
        
        # Save history
        self.history_var = tk.BooleanVar(value=self.settings.get('save_history', True))
        history_check = tk.Checkbutton(section, text="💾 Save listening history",
                                       font=("Arial", 12),
                                       fg='white', bg='#2a1f1a',
                                       selectcolor='#1a0f0a',
                                       activebackground='#2a1f1a',
                                       activeforeground='white',
                                       variable=self.history_var,
                                       command=lambda: self.settings.update({'save_history': self.history_var.get()}))
        history_check.pack(anchor="w", padx=20, pady=(10, 20))
    
    def load_profile_picture(self):
        """Load and display profile picture"""
        pic_path = f"{PROFILE_PICS_FOLDER}/{self.current_user}.png"
        
        if os.path.exists(pic_path):
            img = Image.open(pic_path)
        else:
            # Create default avatar
            img = self.create_default_avatar()
        
        # Resize to 150x150 circle
        img = img.resize((150, 150), Image.Resampling.LANCZOS)
        
        # Make circular
        mask = Image.new('L', (150, 150), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 150, 150), fill=255)
        
        output = Image.new('RGBA', (150, 150), (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        self.profile_photo = ImageTk.PhotoImage(output)
        self.profile_pic_label.config(image=self.profile_photo)
    
    def create_default_avatar(self):
        """Create default profile picture with initials"""
        img = Image.new('RGB', (150, 150), COLORS['primary'])
        draw = ImageDraw.Draw(img)
        
        # Get initials
        initials = self.current_user[0].upper() if self.current_user else 'U'
        if len(self.current_user) > 1:
            initials += self.current_user[1].upper()
        
        # Draw initials (simplified - you may need PIL font for better rendering)
        draw.text((60, 60), initials, fill='white')
        
        return img
    
    def toggle_password_visibility(self, entry, field_type):
        """Toggle password visibility for a specific field"""
        if field_type == 'current':
            self.current_pwd_visible = not self.current_pwd_visible
            if self.current_pwd_visible:
                entry.config(show='')
                self.current_pwd_toggle.config(text='👁‍🗨')
            else:
                entry.config(show='•')
                self.current_pwd_toggle.config(text='👁')
        
        elif field_type == 'new':
            self.new_pwd_visible = not self.new_pwd_visible
            if self.new_pwd_visible:
                entry.config(show='')
                self.new_pwd_toggle.config(text='👁‍🗨')
            else:
                entry.config(show='•')
                self.new_pwd_toggle.config(text='👁')
        
        elif field_type == 'confirm':
            self.confirm_pwd_visible = not self.confirm_pwd_visible
            if self.confirm_pwd_visible:
                entry.config(show='')
                self.confirm_pwd_toggle.config(text='👁‍🗨')
            else:
                entry.config(show='•')
                self.confirm_pwd_toggle.config(text='👁')
    
    def upload_profile_picture(self):
        """Upload new profile picture"""
        file_path = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        
        if file_path:
            try:
                # Copy to profile folder
                dest_path = f"{PROFILE_PICS_FOLDER}/{self.current_user}.png"
                
                # Open, resize, and save
                img = Image.open(file_path)
                img = img.resize((300, 300), Image.Resampling.LANCZOS)
                img.save(dest_path, 'PNG')
                
                # Reload display
                self.load_profile_picture()
                
                messagebox.showinfo("Success", "Profile picture updated!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not upload picture: {e}")
    
    def change_password(self):
        """Change user password"""
        current = self.current_password_entry.get()
        new = self.new_password_entry.get()
        confirm = self.confirm_password_entry.get()
        
        if not current or not new or not confirm:
            messagebox.showerror("Error", "All password fields are required!")
            return
        
        # Verify current password
        current_hash = hashlib.sha256(current.encode()).hexdigest()
        if self.user_data.get('password') != current_hash:
            messagebox.showerror("Error", "Current password is incorrect!")
            return
        
        # Validate new password
        if len(new) < 6:
            messagebox.showerror("Error", "New password must be at least 6 characters!")
            return
        
        if new != confirm:
            messagebox.showerror("Error", "New passwords don't match!")
            return
        
        # Update password
        new_hash = hashlib.sha256(new.encode()).hexdigest()
        users_collection.update_one(
            {'username': self.current_user},
            {'$set': {'password': new_hash, 'password_updated': datetime.now()}}
        )
        
        # Clear fields
        self.current_password_entry.delete(0, tk.END)
        self.new_password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)
        
        messagebox.showinfo("Success", "Password changed successfully!")
    
    def save_all_changes(self):
        """Save all settings"""
        self.save_settings()
        messagebox.showinfo("Success", "All settings saved!")
    
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
    SettingsPage()