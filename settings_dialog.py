"""
Settings and Configuration Dialog for AI Desktop Wellness Companion.
Allows configuring Gemini API key, focus intervals, companion name, and theme.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Callable
from config_manager import COLOR_THEMES, save_config

class SettingsDialog:
    def __init__(self, parent, current_config: Dict[str, Any], gemini_client, on_save_callback: Callable[[Dict[str, Any]], None]):
        self.parent = parent
        self.config = current_config.copy()
        self.gemini_client = gemini_client
        self.on_save_callback = on_save_callback

        theme_name = self.config.get("theme", "pastel_peach")
        self.colors = COLOR_THEMES.get(theme_name, COLOR_THEMES["pastel_peach"])

        self.window = tk.Toplevel(parent)
        self.window.title(f"Wellness Companion Preferences")
        self.window.geometry("440x480")
        self.window.resizable(False, False)
        self.window.configure(bg=self.colors.get("bg_main", "#FFF5E4"))
        self.window.attributes("-topmost", True)

        self._center_window()
        self._build_ui()

    def _center_window(self):
        self.window.update_idletasks()
        w = 440
        h = 480
        px = self.parent.winfo_rootx()
        py = self.parent.winfo_rooty()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        x = max(40, px + (pw // 2) - (w // 2))
        y = max(40, py + (ph // 2) - (h // 2))
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.window, bg=self.colors.get("header_bg", "#FF9494"), pady=10)
        hdr.pack(fill=tk.X)

        tk.Label(
            hdr,
            text="⚙️ Companion Settings & Gemini AI Setup",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors.get("header_bg", "#FF9494"),
            fg="white"
        ).pack()

        body = tk.Frame(self.window, bg=self.colors.get("bg_main", "#FFF5E4"), padx=20, pady=12)
        body.pack(fill=tk.BOTH, expand=True)

        # 1. Gemini API Key Section
        api_group = tk.LabelFrame(
            body,
            text=" 🤖 Gemini API Configuration ",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors.get("bg_main", "#FFF5E4"),
            fg=self.colors.get("text_primary", "#2D3436"),
            padx=10,
            pady=8
        )
        api_group.pack(fill=tk.X, pady=6)

        tk.Label(
            api_group,
            text="Gemini API Key (Leave empty to use Smart Local Mode):",
            font=("Segoe UI", 8),
            bg=self.colors.get("bg_main", "#FFF5E4"),
            fg=self.colors.get("text_secondary", "#636E72")
        ).pack(anchor=tk.W)

        key_frame = tk.Frame(api_group, bg=self.colors.get("bg_main", "#FFF5E4"))
        key_frame.pack(fill=tk.X, pady=4)

        self.entry_key = tk.Entry(key_frame, font=("Segoe UI", 9), show="●")
        self.entry_key.insert(0, self.config.get("api_key", ""))
        self.entry_key.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self.show_key_var = tk.BooleanVar(value=False)
        self.chk_show = tk.Checkbutton(
            key_frame,
            text="Show",
            variable=self.show_key_var,
            font=("Segoe UI", 8),
            bg=self.colors.get("bg_main", "#FFF5E4"),
            command=self._toggle_show_key
        )
        self.chk_show.pack(side=tk.LEFT)

        test_row = tk.Frame(api_group, bg=self.colors.get("bg_main", "#FFF5E4"))
        test_row.pack(fill=tk.X, pady=2)

        self.btn_test_key = tk.Button(
            test_row,
            text="Test API Connection",
            font=("Segoe UI", 8),
            bg=self.colors.get("btn_secondary", "#FFE3E1"),
            fg=self.colors.get("text_primary", "#2D3436"),
            relief=tk.FLAT,
            command=self._test_connection
        )
        self.btn_test_key.pack(side=tk.LEFT)

        self.lbl_test_result = tk.Label(
            test_row,
            text="",
            font=("Segoe UI", 8),
            bg=self.colors.get("bg_main", "#FFF5E4"),
            fg=self.colors.get("text_secondary", "#636E72")
        )
        self.lbl_test_result.pack(side=tk.LEFT, padx=8)

        # 2. Timer Intervals Section
        timer_group = tk.LabelFrame(
            body,
            text=" ⏱ Burnout & Sprint Intervals ",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors.get("bg_main", "#FFF5E4"),
            fg=self.colors.get("text_primary", "#2D3436"),
            padx=10,
            pady=8
        )
        timer_group.pack(fill=tk.X, pady=6)

        # Focus duration
        f_row = tk.Frame(timer_group, bg=self.colors.get("bg_main", "#FFF5E4"))
        f_row.pack(fill=tk.X, pady=2)
        tk.Label(f_row, text="Focus Sprint Duration (mins):", font=("Segoe UI", 8), bg=self.colors.get("bg_main", "#FFF5E4")).pack(side=tk.LEFT)
        self.spin_focus = tk.Spinbox(f_row, from_=5, to=120, width=5)
        self.spin_focus.delete(0, "end")
        self.spin_focus.insert(0, str(self.config.get("work_duration_minutes", 25)))
        self.spin_focus.pack(side=tk.RIGHT)

        # Break duration
        b_row = tk.Frame(timer_group, bg=self.colors.get("bg_main", "#FFF5E4"))
        b_row.pack(fill=tk.X, pady=2)
        tk.Label(b_row, text="Break Rest Duration (mins):", font=("Segoe UI", 8), bg=self.colors.get("bg_main", "#FFF5E4")).pack(side=tk.LEFT)
        self.spin_break = tk.Spinbox(b_row, from_=1, to=30, width=5)
        self.spin_break.delete(0, "end")
        self.spin_break.insert(0, str(self.config.get("break_duration_minutes", 5)))
        self.spin_break.pack(side=tk.RIGHT)

        # Burnout threshold
        bo_row = tk.Frame(timer_group, bg=self.colors.get("bg_main", "#FFF5E4"))
        bo_row.pack(fill=tk.X, pady=2)
        tk.Label(bo_row, text="High Burnout Alert Threshold (mins):", font=("Segoe UI", 8), bg=self.colors.get("bg_main", "#FFF5E4")).pack(side=tk.LEFT)
        self.spin_burnout = tk.Spinbox(bo_row, from_=20, to=180, width=5)
        self.spin_burnout.delete(0, "end")
        self.spin_burnout.insert(0, str(self.config.get("burnout_threshold_minutes", 50)))
        self.spin_burnout.pack(side=tk.RIGHT)

        # 3. Companion Customization
        pet_group = tk.LabelFrame(
            body,
            text=" 🎨 Customization & Theme ",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors.get("bg_main", "#FFF5E4"),
            fg=self.colors.get("text_primary", "#2D3436"),
            padx=10,
            pady=8
        )
        pet_group.pack(fill=tk.X, pady=6)

        p_row = tk.Frame(pet_group, bg=self.colors.get("bg_main", "#FFF5E4"))
        p_row.pack(fill=tk.X, pady=2)
        tk.Label(p_row, text="Companion Name:", font=("Segoe UI", 8), bg=self.colors.get("bg_main", "#FFF5E4")).pack(side=tk.LEFT)
        self.entry_name = tk.Entry(p_row, width=15, font=("Segoe UI", 9))
        self.entry_name.insert(0, self.config.get("pet_name", "Neko"))
        self.entry_name.pack(side=tk.RIGHT)

        t_row = tk.Frame(pet_group, bg=self.colors.get("bg_main", "#FFF5E4"))
        t_row.pack(fill=tk.X, pady=2)
        tk.Label(t_row, text="Color Theme:", font=("Segoe UI", 8), bg=self.colors.get("bg_main", "#FFF5E4")).pack(side=tk.LEFT)
        self.combo_theme = ttk.Combobox(
            t_row,
            values=["pastel_peach", "mint_calm", "lavender_night", "dark_slate"],
            state="readonly",
            width=14
        )
        self.combo_theme.set(self.config.get("theme", "pastel_peach"))
        self.combo_theme.pack(side=tk.RIGHT)

        # Checkboxes
        chk_row = tk.Frame(pet_group, bg=self.colors.get("bg_main", "#FFF5E4"))
        chk_row.pack(fill=tk.X, pady=2)

        self.topmost_var = tk.BooleanVar(value=self.config.get("always_on_top", True))
        tk.Checkbutton(
            chk_row,
            text="Always on Top",
            variable=self.topmost_var,
            font=("Segoe UI", 8),
            bg=self.colors.get("bg_main", "#FFF5E4")
        ).pack(side=tk.LEFT)

        self.sound_var = tk.BooleanVar(value=self.config.get("sound_enabled", True))
        tk.Checkbutton(
            chk_row,
            text="Chime Alert",
            variable=self.sound_var,
            font=("Segoe UI", 8),
            bg=self.colors.get("bg_main", "#FFF5E4")
        ).pack(side=tk.RIGHT)

        # Action Buttons
        act_row = tk.Frame(self.window, bg=self.colors.get("bg_main", "#FFF5E4"), pady=10)
        act_row.pack(fill=tk.X, padx=20)

        tk.Button(
            act_row,
            text="Cancel",
            font=("Segoe UI", 9),
            bg=self.colors.get("btn_secondary", "#FFE3E1"),
            fg=self.colors.get("text_primary", "#2D3436"),
            relief=tk.FLAT,
            padx=12,
            command=self.window.destroy
        ).pack(side=tk.LEFT)

        tk.Button(
            act_row,
            text="Save & Apply",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors.get("btn_primary", "#FF9494"),
            fg="white",
            relief=tk.FLAT,
            padx=16,
            command=self._save
        ).pack(side=tk.RIGHT)

    def _toggle_show_key(self):
        if self.show_key_var.get():
            self.entry_key.config(show="")
        else:
            self.entry_key.config(show="●")

    def _test_connection(self):
        key = self.entry_key.get().strip()
        if not key:
            self.lbl_test_result.config(text="⚠️ Please enter a key first", fg="#E67E22")
            return

        self.lbl_test_result.config(text="Connecting...", fg="#3498DB")
        self.window.update_idletasks()

        # Temporarily test with candidate key
        old_key = self.gemini_client.api_key
        self.gemini_client.set_api_key(key)
        success, msg = self.gemini_client.test_connection()
        if not success:
            self.gemini_client.set_api_key(old_key)
            self.lbl_test_result.config(text=f"❌ Failed: {msg[:25]}...", fg="#E74C3C")
            messagebox.showwarning("Connection Failed", f"Could not connect to Gemini API:\n\n{msg}")
        else:
            self.lbl_test_result.config(text="✅ Connected!", fg="#27AE60")
            messagebox.showinfo("Success", f"Gemini API responded:\n\n\"{msg}\"")

    def _save(self):
        try:
            work_mins = int(self.spin_focus.get())
            break_mins = int(self.spin_break.get())
            burnout_mins = int(self.spin_burnout.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Interval minutes must be valid numbers.")
            return

        self.config["api_key"] = self.entry_key.get().strip()
        self.config["work_duration_minutes"] = max(1, work_mins)
        self.config["break_duration_minutes"] = max(1, break_mins)
        self.config["burnout_threshold_minutes"] = max(10, burnout_mins)
        self.config["pet_name"] = self.entry_name.get().strip() or "Neko"
        self.config["theme"] = self.combo_theme.get()
        self.config["always_on_top"] = self.topmost_var.get()
        self.config["sound_enabled"] = self.sound_var.get()

        save_config(self.config)
        self.on_save_callback(self.config)
        self.window.destroy()
