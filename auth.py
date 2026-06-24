# auth.py - Complete Fixed Version with Email and Seamless Transitions
import tkinter as tk
from tkinter import messagebox
import hashlib
from config import *
from utils import *
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import os
import re

class AuthPage:
    def __init__(self, callback=None):
        self.callback = callback
        self.root = tk.Tk()
        self.root.title("FEMR - Login")
        self.root.state('zoomed')
        self.root.configure(bg='black')
        
        self.is_login = True
        self.create_ui()
        self.root.mainloop()
    
    def create_ui(self):
        # Canvas for background
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='black')
        self.canvas.pack(fill="both", expand=True)
        
        # Force update to get actual size
        self.root.update_idletasks()
        
        # Load background BEFORE creating form
        screen_width = self.root.winfo_width()
        screen_height = self.root.winfo_height()
        self.load_background(screen_width, screen_height)
        
        # Main container
        container_width = 450
        container_height = 600 if not self.is_login else 500
        
        self.main_container = tk.Frame(self.canvas, bg='#1a0f0a', bd=2, relief="solid")
        self.container_win = self.canvas.create_window(
            screen_width // 2,
            screen_height // 2,
            window=self.main_container,
            width=container_width,
            height=container_height
        )
        
        # Build form content
        self.build_form()
        
        # Enter key binding
        self.root.bind('<Return>', lambda e: self.handle_submit())
        
        # Window resize handler
        def on_resize(event=None):
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            self.canvas.coords(self.container_win, w // 2, h // 2)
        
        self.root.bind('<Configure>', on_resize)
    
    def build_form(self):
        """Build the login/signup form content"""
        # Clear container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Title
        title_text = "🎵 Welcome Back!" if self.is_login else "🎵 Create Account"
        tk.Label(self.main_container, text=title_text,
                font=("Arial", 28, "bold"),
                fg=COLORS['primary'], bg='#1a0f0a').pack(pady=(30, 10))
        
        tk.Label(self.main_container, 
                text="Login to continue" if self.is_login else "Sign up to get started",
                font=("Arial", 11),
                fg='#888', bg='#1a0f0a').pack(pady=(0, 30))
        
        # Form container
        form = tk.Frame(self.main_container, bg='#1a0f0a')
        form.pack(padx=40, fill="both", expand=True)
        
        # Username field
        tk.Label(form, text="Username", 
                font=("Arial", 10, "bold"),
                fg='white', bg='#1a0f0a').pack(anchor="w", pady=(0, 5))
        
        # Username entry container - FIXED HEIGHT
        username_container = tk.Frame(form, bg='#2a1f1a', height=42)
        username_container.pack(fill="x", pady=(0, 15))
        username_container.pack_propagate(False)  # Maintain fixed height
        
        self.username_entry = tk.Entry(username_container, font=("Arial", 12),
                                       bg='#2a1f1a', fg='white',
                                       insertbackground='white',
                                       relief="flat", bd=0,
                                       borderwidth=0)
        self.username_entry.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        # Spacer to match eye icon (icon=16px + padx=10px*2 = 36px total)
        tk.Label(username_container, text="", bg='#2a1f1a', width=3).pack(side="right", padx=(0, 10))
        
        self.username_entry.focus()
        
        # Email field (only for signup)
        if not self.is_login:
            tk.Label(form, text="Email", 
                    font=("Arial", 10, "bold"),
                    fg='white', bg='#1a0f0a').pack(anchor="w", pady=(0, 5))
            
            # Email entry container - FIXED HEIGHT
            email_container = tk.Frame(form, bg='#2a1f1a', height=42)
            email_container.pack(fill="x", pady=(0, 15))
            email_container.pack_propagate(False)  # Maintain fixed height
            
            self.email_entry = tk.Entry(email_container, font=("Arial", 12),
                                        bg='#2a1f1a', fg='white',
                                        insertbackground='white',
                                        relief="flat", bd=0,
                                        borderwidth=0)
            self.email_entry.pack(side="left", fill="both", expand=True, padx=(10, 0))
            
            # Spacer to match eye icon
            tk.Label(email_container, text="", bg='#2a1f1a', width=3).pack(side="right", padx=(0, 10))
        
        # Password field
        tk.Label(form, text="Password", 
                font=("Arial", 10, "bold"),
                fg='white', bg='#1a0f0a').pack(anchor="w", pady=(0, 5))
        
        # Password entry container - FIXED HEIGHT
        password_container = tk.Frame(form, bg='#2a1f1a', height=42)
        password_container.pack(fill="x", pady=(0, 15))
        password_container.pack_propagate(False)  # Maintain fixed height
        
        self.password_entry = tk.Entry(password_container, font=("Arial", 12),
                                       bg='#2a1f1a', fg='white',
                                       insertbackground='white',
                                       show='•', relief="flat", bd=0,
                                       borderwidth=0)
        self.password_entry.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        # Show/Hide password toggle
        self.show_password = False
        self.password_toggle = tk.Label(password_container, text="👁", 
                                       font=("Arial", 16),
                                       fg='#888', bg='#2a1f1a',
                                       cursor="hand2", width=3)
        self.password_toggle.pack(side="right", padx=(0, 10))
        self.password_toggle.bind("<Button-1>", lambda e: self.toggle_password_visibility())
        
        # Confirm Password field (only for signup)
        if not self.is_login:
            tk.Label(form, text="Confirm Password", 
                    font=("Arial", 10, "bold"),
                    fg='white', bg='#1a0f0a').pack(anchor="w", pady=(0, 5))
            
            # Confirm password entry container - FIXED HEIGHT
            confirm_container = tk.Frame(form, bg='#2a1f1a', height=42)
            confirm_container.pack(fill="x", pady=(0, 15))
            confirm_container.pack_propagate(False)  # Maintain fixed height
            
            self.confirm_entry = tk.Entry(confirm_container, font=("Arial", 12),
                                          bg='#2a1f1a', fg='white',
                                          insertbackground='white',
                                          show='•', relief="flat", bd=0,
                                          borderwidth=0)
            self.confirm_entry.pack(side="left", fill="both", expand=True, padx=(10, 0))
            
            # Show/Hide confirm password toggle
            self.show_confirm = False
            self.confirm_toggle = tk.Label(confirm_container, text="👁", 
                                          font=("Arial", 16),
                                          fg='#888', bg='#2a1f1a',
                                          cursor="hand2", width=3)
            self.confirm_toggle.pack(side="right", padx=(0, 10))
            self.confirm_toggle.bind("<Button-1>", lambda e: self.toggle_confirm_visibility())
        
        # Submit button
        button_text = "Login" if self.is_login else "Sign Up"
        tk.Button(form, text=button_text,
                 font=("Arial", 13, "bold"),
                 bg=COLORS['primary'], fg="white",
                 bd=0, cursor="hand2", height=2,
                 command=self.handle_submit).pack(fill="x", pady=(10, 20))
        
        # Toggle link
        toggle_frame = tk.Frame(form, bg='#1a0f0a')
        toggle_frame.pack(pady=(0, 20))
        
        if self.is_login:
            tk.Label(toggle_frame, text="Don't have an account?", 
                    font=("Arial", 10), fg='#888', bg='#1a0f0a').pack(side="left")
            
            toggle_btn = tk.Label(toggle_frame, text=" Sign Up", 
                                 font=("Arial", 10, "bold"),
                                 fg=COLORS['primary'], bg='#1a0f0a',
                                 cursor="hand2")
            toggle_btn.pack(side="left")
            toggle_btn.bind("<Button-1>", lambda e: self.toggle_mode())
        else:
            tk.Label(toggle_frame, text="Already have an account?", 
                    font=("Arial", 10), fg='#888', bg='#1a0f0a').pack(side="left")
            
            toggle_btn = tk.Label(toggle_frame, text=" Login", 
                                 font=("Arial", 10, "bold"),
                                 fg=COLORS['primary'], bg='#1a0f0a',
                                 cursor="hand2")
            toggle_btn.pack(side="left")
            toggle_btn.bind("<Button-1>", lambda e: self.toggle_mode())
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        self.show_password = not self.show_password
        if self.show_password:
            self.password_entry.config(show='')
            self.password_toggle.config(text='👁‍🗨', fg='#ff6b35')  # Open eye, orange
        else:
            self.password_entry.config(show='•')
            self.password_toggle.config(text='👁', fg='#888')  # Closed eye, gray
    
    def toggle_confirm_visibility(self):
        """Toggle confirm password visibility"""
        self.show_confirm = not self.show_confirm
        if self.show_confirm:
            self.confirm_entry.config(show='')
            self.confirm_toggle.config(text='👁‍🗨', fg='#ff6b35')  # Open eye, orange
        else:
            self.confirm_entry.config(show='•')
            self.confirm_toggle.config(text='👁', fg='#888')  # Closed eye, gray
    
    def toggle_mode(self):
        """Toggle between login and signup mode"""
        self.is_login = not self.is_login
        
        # Get current screen dimensions
        screen_width = self.root.winfo_width()
        screen_height = self.root.winfo_height()
        
        # Calculate new container height
        container_width = 450
        container_height = 600 if not self.is_login else 500
        
        # Delete old container from canvas
        if hasattr(self, 'container_win'):
            self.canvas.delete(self.container_win)
        
        # Destroy old container widget
        if hasattr(self, 'main_container'):
            self.main_container.destroy()
        
        # Create new container
        self.main_container = tk.Frame(self.canvas, bg='#1a0f0a', bd=2, relief="solid")
        self.container_win = self.canvas.create_window(
            screen_width // 2,
            screen_height // 2,
            window=self.main_container,
            width=container_width,
            height=container_height
        )
        
        # Build form content
        self.build_form()
    
    def handle_submit(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields!")
            return
        
        if self.is_login:
            self.login(username, password)
        else:
            email = self.email_entry.get().strip()
            confirm = self.confirm_entry.get().strip()
            self.signup(username, email, password, confirm)
    
    def login(self, username, password):
        # Check admin credentials first
        if username == "Admin" and password == "admin123":
            print(" Admin logged in!")
            self.seamless_transition_to_admin()
            return
        
        # Check database for regular user
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = users_collection.find_one({
            'username': username,
            'password': password_hash
        })
        
        if user:
            print(f" User '{username}' logged in!")
            self.seamless_transition_to_home(username)
        else:
            messagebox.showerror("Error", "Invalid username or password!")
    
    def signup(self, username, email, password, confirm):
        # Validation
        if not email:
            messagebox.showerror("Error", "Please enter your email!")
            return
        
        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            messagebox.showerror("Error", "Please enter a valid email address!")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters!")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        # Check if username already exists
        if users_collection.find_one({'username': username}):
            messagebox.showerror("Error", "Username already exists!")
            return
        
        # Check if username is "Admin" (reserved)
        if username.lower() == "admin":
            messagebox.showerror("Error", "Username 'Admin' is reserved!")
            return
        
        # Check if email already exists
        if users_collection.find_one({'email': email}):
            messagebox.showerror("Error", "Email already registered!")
            return
        
        # Create user
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        users_collection.insert_one({
            'username': username,
            'email': email,
            'password': password_hash
        })
        
        messagebox.showinfo("Success", "Account created successfully!")
        self.is_login = True
        self.toggle_mode()
    
    def seamless_transition_to_admin(self):
        """Seamless transition to admin dashboard - NO FLICKER"""
        from admin_panel import AdminDashboard
        
        # Hide window immediately to prevent flicker
        self.root.withdraw()
        self.root.update()
        
        # Small delay to ensure visual smoothness
        self.root.after(10, self._complete_admin_transition)
    
    def _complete_admin_transition(self):
        """Complete transition to admin"""
        from admin_panel import AdminDashboard
        
        # Destroy after hiding
        self.root.quit()
        self.root.destroy()
        
        # Launch admin dashboard
        AdminDashboard()
    
    def seamless_transition_to_home(self, username):
        """Seamless transition to home page - NO FLICKER"""
        # Hide window immediately to prevent flicker
        self.root.withdraw()
        self.root.update()
        
        # Small delay to ensure visual smoothness
        self.root.after(10, lambda: self._complete_home_transition(username))
    
    def _complete_home_transition(self, username):
        """Complete transition to home page"""
        try:
            from ui_components import HomePage  # FIXED: Import from ui_components
            
            # Destroy after hiding
            self.root.quit()
            self.root.destroy()
            
            # Try with username first, fallback to no parameter
            try:
                HomePage(username)
            except TypeError:
                # HomePage doesn't accept username
                print(f"Note: HomePage doesn't accept username parameter, launching without it")
                HomePage()
                
        except Exception as e:
            print(f"Error launching home page: {e}")
            import traceback
            traceback.print_exc()
    
    def load_background(self, w=None, h=None):
        try:
            # Get dimensions
            if w is None or h is None:
                w = self.canvas.winfo_width() or self.root.winfo_screenwidth()
                h = self.canvas.winfo_height() or self.root.winfo_screenheight()
            
            # Try to load background.jpg
            if os.path.exists('background.jpg'):
                img = Image.open('background.jpg')
            else:
                # Create gradient background if file not found
                img = self.create_gradient_bg()
            
            # Resize and crop to fit screen
            iw, ih = img.size
            scale = max(w / iw, h / ih)
            img = img.resize((int(iw * scale), int(ih * scale)), Image.Resampling.LANCZOS)
            
            left = (img.width - w) // 2
            top = (img.height - h) // 2
            img = img.crop((left, top, left + w, top + h))
            
            # Apply blur and darkening
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
            img = ImageEnhance.Brightness(img).enhance(0.75)
            
            # Store reference to prevent garbage collection
            self.bg_image = ImageTk.PhotoImage(img)
            
            # Delete old background if exists
            if hasattr(self, 'bg_image_id'):
                self.canvas.delete(self.bg_image_id)
            
            # Create new background
            self.bg_image_id = self.canvas.create_image(
                w // 2, h // 2, 
                image=self.bg_image, 
                anchor='center'
            )
            
            # Send background to back
            self.canvas.tag_lower(self.bg_image_id)
            
        except Exception as e:
            print(f"BG error: {e}")
            import traceback
            traceback.print_exc()
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

def main():
    print("🎵 EmoTune - Starting...")
    print("✅ Connected to MongoDB")
    print("🔐 Please login or sign up")
    AuthPage()

if __name__ == "__main__":
    main()