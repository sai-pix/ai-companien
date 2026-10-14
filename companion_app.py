"""
Main Desktop Wellness Companion Application.
An interactive, AI-driven floating desktop companion designed to combat burnout,
anxiety, and digital fatigue with Gemini AI integration.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
import os
import sys

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

from config_manager import load_config, save_config, COLOR_THEMES
from gemini_client import GeminiWellnessClient
from burnout_detector import BurnoutDetector
from breathing_exercise import BreathingModal
from stretch_guide import StretchModal
from settings_dialog import SettingsDialog

class DesktopWellnessCompanion:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.config = load_config()

        theme_name = self.config.get("theme", "pastel_peach")
        self.colors = COLOR_THEMES.get(theme_name, COLOR_THEMES["pastel_peach"])

        # Core Engines
        self.gemini = GeminiWellnessClient(
            api_key=self.config.get("api_key", ""),
            model_name=self.config.get("model_name", "gemini-2.5-flash"),
            pet_name=self.config.get("pet_name", "Neko")
        )
        self.detector = BurnoutDetector(
            work_duration_mins=self.config.get("work_duration_minutes", 25),
            break_duration_mins=self.config.get("break_duration_minutes", 5),
            burnout_threshold_mins=self.config.get("burnout_threshold_minutes", 50)
        )

        # Restore daily counts from config
        self.detector.water_count = self.config.get("daily_water_count", 0)
        self.detector.stretch_count = self.config.get("daily_stretch_count", 0)
        self.detector.breathing_count = self.config.get("daily_breathing_count", 0)

        # Window Setup
        self.root.title("AI Desktop Wellness Companion")
        self.is_collapsed = False
        self.width = 330
        self.expanded_height = 490
        self.collapsed_height = 130

        # Position near bottom-right corner of screen
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        start_x = screen_w - self.width - 40
        start_y = screen_h - self.expanded_height - 60

        self.root.geometry(f"{self.width}x{self.expanded_height}+{start_x}+{start_y}")
        self.root.overrideredirect(True)  # Frameless floating design
        self.root.attributes("-topmost", self.config.get("always_on_top", True))
        self.root.configure(bg=self.colors.get("bg_main", "#FFF5E4"))

        # Window Dragging State
        self.drag_x = 0
        self.drag_y = 0

        # Cat Avatar Animation States
        self.cat_state = "NORMAL"  # NORMAL, PURRING, TIRED, BREATHING, SLEEPING
        self.blink_active = False
        self.petting_active = False

        self.cat_sprites = {
            "NORMAL": ["(=^ ◡ ^=)", "(=^..^=)", "(=^ ◡ ^=)"],
            "BLINK": ["( - ◡ - )", "( - .. - )"],
            "PURRING": ["(=^ω^=) ✨", "(=^o^=) 💖", "(=^ ◡ ^=) 🐾"],
            "TIRED": ["(=☉ ‿ ☉=) ⚠️", "(=-..-=)", "(=；ω；=)"],
            "BREATHING": ["( ˘ ᵕ ˘ ) 🧘", "(=^ ◡ ^=) 🌸"],
            "SLEEPING": ["( - ‿ - ) zZz", "( - ω - ) zZz"]
        }

        self.is_pill_mode = False
        self.root.bind("<Escape>", lambda e: self._minimize_to_pill() if not self.is_pill_mode else self._restore_from_pill())

        # Build UI Components
        self._build_ui()

        # Start loops
        self._timer_tick()
        self._blink_tick()

    def _play_chime(self):
        if self.config.get("sound_enabled", True):
            if HAS_WINSOUND:
                try:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception:
                    self.root.bell()
            else:
                self.root.bell()

    def _build_ui(self):
        # 1. Header / Drag bar
        self.header = tk.Frame(self.root, bg=self.colors.get("header_bg", "#FF9494"), height=26, cursor="fleur")
        self.header.pack(fill=tk.X)
        self.header.bind("<Button-1>", self._start_drag)
        self.header.bind("<B1-Motion>", self._on_drag)

        # Pet name & Status Icon in Header
        self.lbl_head_title = tk.Label(
            self.header,
            text=f" 🐾 {self.config.get('pet_name', 'Neko')} Companion",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors.get("header_bg", "#FF9494"),
            fg="white"
        )
        self.lbl_head_title.pack(side=tk.LEFT, padx=6)
        self.lbl_head_title.bind("<Button-1>", self._start_drag)
        self.lbl_head_title.bind("<B1-Motion>", self._on_drag)

        # Header Action Buttons
        btn_close = tk.Button(
            self.header, text="✕", font=("Segoe UI", 8, "bold"),
            bg=self.colors.get("header_bg", "#FF9494"), fg="white", bd=0, padx=6,
            command=self._on_close
        )
        btn_close.pack(side=tk.RIGHT)

        self.btn_collapse = tk.Button(
            self.header, text="▲", font=("Segoe UI", 8),
            bg=self.colors.get("header_bg", "#FF9494"), fg="white", bd=0, padx=6,
            command=self._toggle_collapse
        )
        self.btn_collapse.pack(side=tk.RIGHT)

        self.btn_minimize = tk.Button(
            self.header, text="—", font=("Segoe UI", 8, "bold"),
            bg=self.colors.get("header_bg", "#FF9494"), fg="white", bd=0, padx=6,
            command=self._minimize_to_pill
        )
        self.btn_minimize.pack(side=tk.RIGHT)

        self.btn_pin = tk.Button(
            self.header, text="📌", font=("Segoe UI", 8),
            bg=self.colors.get("header_bg", "#FF9494"), fg="white", bd=0, padx=4,
            command=self._toggle_pin
        )
        self.btn_pin.pack(side=tk.RIGHT)

        # 2. Main Body Container
        self.main_body = tk.Frame(self.root, bg=self.colors.get("bg_main", "#FFF5E4"), padx=12, pady=6)
        self.main_body.pack(fill=tk.BOTH, expand=True)

        # 3. Cat Avatar & Quick Status Card
        self.avatar_card = tk.Frame(self.main_body, bg=self.colors.get("bg_card", "#FFE3E1"), padx=8, pady=6)
        self.avatar_card.pack(fill=tk.X, pady=(2, 6))

        # Cat Avatar display
        self.lbl_cat = tk.Label(
            self.avatar_card,
            text="(=^ ◡ ^=)",
            font=("Courier New", 20, "bold"),
            bg=self.colors.get("bg_card", "#FFE3E1"),
            fg=self.colors.get("text_primary", "#2D3436"),
            cursor="hand2"
        )
        self.lbl_cat.pack(pady=2)
        self.lbl_cat.bind("<Button-1>", lambda e: self._pet_cat())

        lbl_pet_hint = tk.Label(
            self.avatar_card,
            text="*click to pet & get instant wellness advice*",
            font=("Segoe UI", 7, "italic"),
            bg=self.colors.get("bg_card", "#FFE3E1"),
            fg=self.colors.get("text_secondary", "#636E72")
        )
        lbl_pet_hint.pack()

        # Status / Speech bubble
        self.lbl_speech = tk.Label(
            self.avatar_card,
            text="Purring along with your workflow... You've got this!",
            font=("Segoe UI", 8),
            bg=self.colors.get("bg_card", "#FFE3E1"),
            fg=self.colors.get("text_primary", "#2D3436"),
            wraplength=280,
            justify=tk.CENTER
        )
        self.lbl_speech.pack(pady=4)

        # AI badge (Gemini Live vs Smart Local)
        self.lbl_ai_badge = tk.Label(
            self.avatar_card,
            text="🟢 Gemini AI Live" if self.gemini.has_api_key() else "🟣 Smart Local Mode",
            font=("Segoe UI", 7, "bold"),
            bg=self.colors.get("bg_card", "#FFE3E1"),
            fg="#27AE60" if self.gemini.has_api_key() else "#8E44AD"
        )
        self.lbl_ai_badge.pack()

        # 4. Burnout Risk Gauge & Focus Timer Section
        self.metrics_frame = tk.Frame(self.main_body, bg=self.colors.get("bg_main", "#FFF5E4"))
        self.metrics_frame.pack(fill=tk.X, pady=2)

        # Row with Focus Timer and State
        row_time = tk.Frame(self.metrics_frame, bg=self.colors.get("bg_main", "#FFF5E4"))
        row_time.pack(fill=tk.X)

        self.lbl_mode_state = tk.Label(
            row_time,
            text="🌱 Focus Sprint",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors.get("bg_main", "#FFF5E4"),
            fg=self.colors.get("accent", "#FF6B6B")
        )
        self.lbl_mode_state.pack(side=tk.LEFT)

        self.lbl_timer = tk.Label(
            row_time,
            text="00:00",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors.get("bg_main", "#FFF5E4"),
            fg=self.colors.get("text_primary", "#2D3436")
        )
        self.lbl_timer.pack(side=tk.RIGHT)

        # Burnout Risk Progress Bar
        self.progress_frame = tk.Frame(self.metrics_frame, bg=self.colors.get("bg_main", "#FFF5E4"))
        self.progress_frame.pack(fill=tk.X, pady=3)

        self.lbl_burnout_text = tk.Label(
            self.progress_frame,
            text="Burnout Risk: 10% (Low)",
            font=("Segoe UI", 8),
            bg=self.colors.get("bg_main", "#FFF5E4"),
            fg=self.colors.get("text_secondary", "#636E72")
        )
        self.lbl_burnout_text.pack(anchor=tk.W)

        self.progress_canvas = tk.Canvas(
            self.progress_frame,
            height=8,
            bg=self.colors.get("progress_bg", "#F0E4D7"),
            highlightthickness=0
        )
        self.progress_canvas.pack(fill=tk.X, pady=1)

        # Break / Work Toggle Button
        self.btn_toggle_break = tk.Button(
            self.metrics_frame,
            text="☕ Take a Break",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors.get("btn_secondary", "#FFE3E1"),
            fg=self.colors.get("text_primary", "#2D3436"),
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self._toggle_work_break
        )
        self.btn_toggle_break.pack(fill=tk.X, pady=3)

        # 5. Quick Wellness Actions Bar
        self.actions_card = tk.Frame(self.main_body, bg=self.colors.get("bg_main", "#FFF5E4"))
        self.actions_card.pack(fill=tk.X, pady=2)

        btn_grid = tk.Frame(self.actions_card, bg=self.colors.get("bg_main", "#FFF5E4"))
        btn_grid.pack(fill=tk.X)

        self.btn_breathe = tk.Button(
            btn_grid, text="🌬️ Breathe", font=("Segoe UI", 8),
            bg=self.colors.get("btn_primary", "#FF9494"), fg="white", relief=tk.FLAT,
            padx=6, pady=3, cursor="hand2", command=self._start_breathing
        )
        self.btn_breathe.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        self.btn_stretch = tk.Button(
            btn_grid, text="🤸 Stretch", font=("Segoe UI", 8),
            bg=self.colors.get("btn_primary", "#FF9494"), fg="white", relief=tk.FLAT,
            padx=6, pady=3, cursor="hand2", command=self._open_stretch
        )
        self.btn_stretch.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.btn_water = tk.Button(
            btn_grid, text=f"💧 +Water ({self.detector.water_count})", font=("Segoe UI", 8),
            bg=self.colors.get("btn_primary", "#FF9494"), fg="white", relief=tk.FLAT,
            padx=6, pady=3, cursor="hand2", command=self._log_water
        )
        self.btn_water.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 2))

        self.btn_settings = tk.Button(
            btn_grid, text="⚙️", font=("Segoe UI", 8),
            bg=self.colors.get("btn_secondary", "#FFE3E1"), fg=self.colors.get("text_primary", "#2D3436"),
            relief=tk.FLAT, padx=6, pady=3, cursor="hand2", command=self._open_settings
        )
        self.btn_settings.pack(side=tk.RIGHT, padx=(2, 0))

        # 6. Interactive Chat / Check-in Drawer
        self.chat_drawer = tk.LabelFrame(
            self.main_body,
            text=f" 💬 Chat with {self.config.get('pet_name', 'Neko')} ",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors.get("bg_main", "#FFF5E4"),
            fg=self.colors.get("text_primary", "#2D3436"),
            padx=6,
            pady=4
        )
        self.chat_drawer.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        chat_input_row = tk.Frame(self.chat_drawer, bg=self.colors.get("bg_main", "#FFF5E4"))
        chat_input_row.pack(fill=tk.X)

        self.entry_chat = tk.Entry(
            chat_input_row,
            font=("Segoe UI", 8),
            relief=tk.SOLID,
            bd=1
        )
        self.entry_chat.insert(0, "Feeling tired or stressed? Tell me...")
        self.entry_chat.bind("<FocusIn>", self._clear_placeholder)
        self.entry_chat.bind("<Return>", lambda e: self._send_chat())
        self.entry_chat.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.btn_send = tk.Button(
            chat_input_row,
            text="Ask",
            font=("Segoe UI", 8, "bold"),
            bg=self.colors.get("accent", "#FF6B6B"),
            fg="white",
            relief=tk.FLAT,
            padx=8,
            command=self._send_chat
        )
        self.btn_send.pack(side=tk.RIGHT)

        # Quick Mood Buttons row
        mood_row = tk.Frame(self.chat_drawer, bg=self.colors.get("bg_main", "#FFF5E4"))
        mood_row.pack(fill=tk.X, pady=(4, 0))

        tk.Button(
            mood_row, text="😫 Overwhelmed", font=("Segoe UI", 7),
            bg=self.colors.get("bg_card", "#FFE3E1"), fg=self.colors.get("text_primary", "#2D3436"),
            relief=tk.FLAT, bd=0, command=lambda: self._quick_mood("I feel overwhelmed and anxious")
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        tk.Button(
            mood_row, text="🥱 Eye Strain", font=("Segoe UI", 7),
            bg=self.colors.get("bg_card", "#FFE3E1"), fg=self.colors.get("text_primary", "#2D3436"),
            relief=tk.FLAT, bd=0, command=lambda: self._quick_mood("My eyes hurt from screen fatigue")
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        tk.Button(
            mood_row, text="✨ Got Stuck", font=("Segoe UI", 7),
            bg=self.colors.get("bg_card", "#FFE3E1"), fg=self.colors.get("text_primary", "#2D3436"),
            relief=tk.FLAT, bd=0, command=lambda: self._quick_mood("I am stuck on a tough bug and frustrated")
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

    def _clear_placeholder(self, event):
        if "Feeling tired or stressed?" in self.entry_chat.get():
            self.entry_chat.delete(0, tk.END)

    def _quick_mood(self, mood_text: str):
        self.entry_chat.delete(0, tk.END)
        self.entry_chat.insert(0, mood_text)
        self._send_chat()

    def _send_chat(self):
        msg = self.entry_chat.get().strip()
        if not msg or "Feeling tired or stressed?" in msg:
            return

        self.entry_chat.delete(0, tk.END)
        self.lbl_speech.config(text=f"Thinking... (=^..^=)", fg=self.colors.get("text_secondary", "#636E72"))
        self.root.update_idletasks()

        # Record sentiment estimation
        msg_lower = msg.lower()
        if any(w in msg_lower for w in ["stress", "anxious", "tired", "bug", "hate", "stuck", "hurt", "overwhelm"]):
            self.detector.record_sentiment(-0.8)
        elif any(w in msg_lower for w in ["good", "happy", "great", "done", "fixed"]):
            self.detector.record_sentiment(0.8)

        # Get context
        context = self.detector.calculate_burnout_metrics()

        # Request reply asynchronously or fast
        reply, is_live = self.gemini.chat(msg, context)
        self.lbl_speech.config(text=reply, fg=self.colors.get("text_primary", "#2D3436"))

        # Update badge
        self._update_ai_badge(is_live)

        # Animate cat
        self._trigger_temporary_state("PURRING", duration_secs=3)

    def _pet_cat(self):
        self._play_chime()
        context = self.detector.calculate_burnout_metrics()
        reply, is_live = self.gemini.generate_burnout_checkin(context)
        self.lbl_speech.config(text=reply, fg=self.colors.get("accent", "#FF6B6B"))
        self._update_ai_badge(is_live)
        self._trigger_temporary_state("PURRING", duration_secs=3)

    def _log_water(self):
        self.detector.log_action("water")
        self.config["daily_water_count"] = self.detector.water_count
        save_config(self.config)
        self.btn_water.config(text=f"💧 +Water ({self.detector.water_count})")
        self.lbl_speech.config(text=f"(=^ ◡ ^=) *slurp!* Hydration logged ({self.detector.water_count} glasses today). Your brain thanks you!", fg="#27AE60")
        self._trigger_temporary_state("PURRING", duration_secs=2)

    def _start_breathing(self):
        self.cat_state = "BREATHING"
        self.lbl_cat.config(text="( ˘ ᵕ ˘ ) 🧘")
        self.lbl_speech.config(text="Taking deep, rhythmic breaths with you...")

        def on_complete():
            self.detector.log_action("breathing")
            self.config["daily_breathing_count"] = self.detector.breathing_count
            save_config(self.config)
            self._play_chime()
            self.lbl_speech.config(text="✨ Wonderful breath session completed! Feeling centered.", fg="#27AE60")
            self._trigger_temporary_state("PURRING", duration_secs=4)

        BreathingModal(self.root, self.colors, pet_name=self.config.get("pet_name", "Neko"), on_complete_callback=on_complete)

    def _open_stretch(self):
        def on_complete():
            self.detector.log_action("stretch")
            self.config["daily_stretch_count"] = self.detector.stretch_count
            save_config(self.config)
            self._play_chime()
            self.lbl_speech.config(text="🐾 Great stretching! Blood flow restored.", fg="#27AE60")
            self._trigger_temporary_state("PURRING", duration_secs=3)

        StretchModal(self.root, self.colors, pet_name=self.config.get("pet_name", "Neko"), on_complete_callback=on_complete)

    def _open_settings(self):
        def on_save(new_config):
            self.config = new_config
            self.gemini.set_api_key(new_config.get("api_key", ""))
            self.gemini.set_pet_name(new_config.get("pet_name", "Neko"))
            self.detector.set_durations(
                work_mins=new_config.get("work_duration_minutes", 25),
                break_mins=new_config.get("break_duration_minutes", 5),
                burnout_mins=new_config.get("burnout_threshold_minutes", 50)
            )
            self.root.attributes("-topmost", new_config.get("always_on_top", True))
            self.lbl_head_title.config(text=f" 🐾 {new_config.get('pet_name', 'Neko')} Companion")
            self._update_ai_badge(self.gemini.has_api_key())
            # Reload theme
            theme_name = new_config.get("theme", "pastel_peach")
            self.colors = COLOR_THEMES.get(theme_name, COLOR_THEMES["pastel_peach"])
            self._apply_theme()

        SettingsDialog(self.root, self.config, self.gemini, on_save)

    def _apply_theme(self):
        bg = self.colors.get("bg_main", "#FFF5E4")
        card = self.colors.get("bg_card", "#FFE3E1")
        hdr = self.colors.get("header_bg", "#FF9494")
        text = self.colors.get("text_primary", "#2D3436")

        self.root.configure(bg=bg)
        self.header.configure(bg=hdr)
        self.lbl_head_title.configure(bg=hdr)
        self.btn_collapse.configure(bg=hdr)
        self.btn_pin.configure(bg=hdr)
        self.main_body.configure(bg=bg)
        self.avatar_card.configure(bg=card)
        self.lbl_cat.configure(bg=card, fg=text)
        self.lbl_speech.configure(bg=card)
        self.lbl_ai_badge.configure(bg=card)
        self.metrics_frame.configure(bg=bg)
        self.progress_frame.configure(bg=bg)
        self.actions_card.configure(bg=bg)
        self.chat_drawer.configure(bg=bg, fg=text)

    def _toggle_work_break(self):
        if self.detector.current_state == "WORKING":
            self.detector.start_break()
            self.lbl_mode_state.config(text="☕ On Break", fg="#27AE60")
            self.btn_toggle_break.config(text="▶ Return to Focus", bg=self.colors.get("btn_primary", "#FF9494"), fg="white")
            self.lbl_speech.config(text="Enjoy your break! Step away, hydrate, and relax your mind.")
            self.cat_state = "SLEEPING"
            self.lbl_cat.config(text="( - ‿ - ) zZz")
        else:
            self.detector.resume_work()
            self.lbl_mode_state.config(text="🌱 Focus Sprint", fg=self.colors.get("accent", "#FF6B6B"))
            self.btn_toggle_break.config(text="☕ Take a Break", bg=self.colors.get("btn_secondary", "#FFE3E1"), fg=self.colors.get("text_primary", "#2D3436"))
            self.lbl_speech.config(text="Welcome back! Let's do great work with calm focus.")
            self.cat_state = "NORMAL"

    def _toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.btn_collapse.config(text="▼")
            self.main_body.pack_forget()
            self.root.geometry(f"{self.width}x{self.collapsed_height}")
            # Mini body for collapsed state
            self.mini_frame = tk.Frame(self.root, bg=self.colors.get("bg_main", "#FFF5E4"), padx=10, pady=4)
            self.mini_frame.pack(fill=tk.BOTH, expand=True)

            self.lbl_mini_cat = tk.Label(
                self.mini_frame,
                text="(=^ ◡ ^=)",
                font=("Courier New", 14, "bold"),
                bg=self.colors.get("bg_main", "#FFF5E4"),
                fg=self.colors.get("text_primary", "#2D3436"),
                cursor="hand2"
            )
            self.lbl_mini_cat.pack(side=tk.LEFT, padx=6)
            self.lbl_mini_cat.bind("<Button-1>", lambda e: self._pet_cat())

            self.lbl_mini_timer = tk.Label(
                self.mini_frame,
                text="Focus: 00:00",
                font=("Segoe UI", 9, "bold"),
                bg=self.colors.get("bg_main", "#FFF5E4"),
                fg=self.colors.get("accent", "#FF6B6B")
            )
            self.lbl_mini_timer.pack(side=tk.LEFT, padx=6)
        else:
            self.btn_collapse.config(text="▲")
            if hasattr(self, "mini_frame"):
                self.mini_frame.destroy()
            self.main_body.pack(fill=tk.BOTH, expand=True)
            self.root.geometry(f"{self.width}x{self.expanded_height}")

    def _toggle_pin(self):
        current = self.config.get("always_on_top", True)
        new_val = not current
        self.config["always_on_top"] = new_val
        self.root.attributes("-topmost", new_val)
        self.btn_pin.config(fg="white" if new_val else "#CCCCCC")
        save_config(self.config)

    def _minimize_to_pill(self):
        """Minimizes the companion to an ultra-compact floating 44x44 paw pill."""
        self.is_pill_mode = True
        self.header.pack_forget()
        self.main_body.pack_forget()
        if hasattr(self, "mini_frame") and self.mini_frame.winfo_exists():
            self.mini_frame.pack_forget()

        pill_w = 46
        pill_h = 46
        # Align to bottom-right or keep near edge
        cur_x = self.root.winfo_x() + (self.width - pill_w)
        cur_y = self.root.winfo_y() + (self.expanded_height - pill_h)
        self.root.geometry(f"{pill_w}x{pill_h}+{cur_x}+{cur_y}")

        self.pill_frame = tk.Frame(self.root, bg=self.colors.get("header_bg", "#FF9494"), cursor="hand2")
        self.pill_frame.pack(fill=tk.BOTH, expand=True)

        self.lbl_pill_icon = tk.Label(
            self.pill_frame,
            text="🐾",
            font=("Segoe UI", 16),
            bg=self.colors.get("header_bg", "#FF9494"),
            fg="white",
            cursor="hand2"
        )
        self.lbl_pill_icon.pack(expand=True)

        # Click to restore
        self.lbl_pill_icon.bind("<Button-1>", lambda e: self._restore_from_pill())
        self.pill_frame.bind("<Button-1>", lambda e: self._restore_from_pill())

        # Allow dragging the mini pill too
        self.lbl_pill_icon.bind("<Button-3>", lambda e: self._restore_from_pill())

    def _restore_from_pill(self):
        """Restores the full companion from pill mode."""
        self.is_pill_mode = False
        if hasattr(self, "pill_frame"):
            self.pill_frame.destroy()

        self.header.pack(fill=tk.X)
        if self.is_collapsed:
            if hasattr(self, "mini_frame"):
                self.mini_frame.pack(fill=tk.BOTH, expand=True)
            self.root.geometry(f"{self.width}x{self.collapsed_height}")
        else:
            self.main_body.pack(fill=tk.BOTH, expand=True)
            self.root.geometry(f"{self.width}x{self.expanded_height}")

    def _update_ai_badge(self, is_live: bool):
        if is_live:
            self.lbl_ai_badge.config(text="🟢 Gemini AI Live", fg="#27AE60")
        else:
            self.lbl_ai_badge.config(text="🟣 Smart Local Mode", fg="#8E44AD")

    def _trigger_temporary_state(self, state_name: str, duration_secs: int = 3):
        self.cat_state = state_name
        sprites = self.cat_sprites.get(state_name, ["(=^ ◡ ^=)"])
        self.lbl_cat.config(text=random.choice(sprites))

        def revert():
            if self.cat_state == state_name:
                self.cat_state = "NORMAL"
                self.lbl_cat.config(text=random.choice(self.cat_sprites["NORMAL"]))

        self.root.after(duration_secs * 1000, revert)

    def _blink_tick(self):
        # Trigger subtle blink when in normal state
        if self.cat_state == "NORMAL":
            self.lbl_cat.config(text=random.choice(self.cat_sprites["BLINK"]))
            self.root.after(220, self._unblink)
        next_blink = random.randint(3500, 6500)
        self.root.after(next_blink, self._blink_tick)

    def _unblink(self):
        if self.cat_state == "NORMAL":
            self.lbl_cat.config(text=random.choice(self.cat_sprites["NORMAL"]))

    def _timer_tick(self):
        elapsed = self.detector.get_elapsed_seconds()
        mins, secs = divmod(elapsed, 60)

        # Update Timer label
        if self.detector.current_state == "WORKING":
            timer_str = f"{mins:02d}:{secs:02d}"
        else:
            timer_str = f"Break: {mins:02d}:{secs:02d}"
        self.lbl_timer.config(text=timer_str)

        if hasattr(self, "lbl_mini_timer") and self.lbl_mini_timer.winfo_exists():
            self.lbl_mini_timer.config(text=timer_str)

        # Update Burnout Metrics
        metrics = self.detector.calculate_burnout_metrics()
        score = metrics["score"]
        level = metrics["level"]
        color = metrics["color"]

        self.lbl_burnout_text.config(
            text=f"Burnout Risk: {score}% ({level} - {metrics['status_desc']})",
            fg=color
        )

        # Draw progress bar
        self._draw_burnout_bar(score, color)

        # Update cat state if high burnout
        if level == "High" and self.cat_state == "NORMAL":
            self.cat_state = "TIRED"
            self.lbl_cat.config(text=random.choice(self.cat_sprites["TIRED"]))

        # Check if work sprint finished
        if self.detector.is_work_time_up():
            self._play_chime()
            self._trigger_break_notification()

        # Check if break finished
        if self.detector.is_break_time_up():
            self._play_chime()
            self.lbl_speech.config(text="(=^ ◡ ^=) Break completed! Ready to begin a fresh focus session?", fg="#27AE60")
            self._toggle_work_break()

        # Schedule next tick every second
        self.root.after(1000, self._timer_tick)

    def _draw_burnout_bar(self, score: int, color: str):
        self.progress_canvas.delete("all")
        w = self.progress_canvas.winfo_width()
        if w <= 1:
            w = 280
        h = 8
        fill_w = int((score / 100.0) * w)
        self.progress_canvas.create_rectangle(0, 0, fill_w, h, fill=color, outline="")

    def _trigger_break_notification(self):
        context = self.detector.calculate_burnout_metrics()
        tip, is_live = self.gemini.generate_burnout_checkin(context)
        self.lbl_speech.config(text=f"⏰ Break Time! {tip}", fg="#E74C3C")
        self._update_ai_badge(is_live)
        self._toggle_work_break()

    # Window Dragging Event Handlers
    def _start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() + (event.x - self.drag_x)
        y = self.root.winfo_y() + (event.y - self.drag_y)
        self.root.geometry(f"+{x}+{y}")

    def _on_close(self):
        # Save daily metrics
        self.config["daily_water_count"] = self.detector.water_count
        self.config["daily_stretch_count"] = self.detector.stretch_count
        self.config["daily_breathing_count"] = self.detector.breathing_count
        save_config(self.config)
        self.root.destroy()
