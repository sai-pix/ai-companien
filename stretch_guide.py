"""
Micro-Stretch and Ergonomics Guide for AI Desktop Wellness Companion.
Offers targeted physical routines to combat desk fatigue and RSI.
"""

import tkinter as tk

STRETCH_ROUTINES = [
    {
        "title": "20-20-20 Eye Reset",
        "cat_art": "(=☉ ‿ ☉=)",
        "duration": "20 seconds",
        "steps": [
            "1. Find an object roughly 20 feet (6 meters) away.",
            "2. Focus your gaze softly on it for at least 20 seconds.",
            "3. Blink rapidly 10 times to naturally re-moisturize your eyes.",
            "4. Gently rub your palms together and cup them over closed eyes."
        ],
        "benefit": "Relieves ciliary muscle spasm and computer vision syndrome."
    },
    {
        "title": "Wrist & Finger Decompression",
        "cat_art": "(=^..^=) ฅ/ᐠ｡ᆽ｡ᐟ ฅ",
        "duration": "45 seconds",
        "steps": [
            "1. Extend one arm forward, palm facing out like a 'stop' sign.",
            "2. Use the other hand to gently pull your fingers back for 15s.",
            "3. Flip palm downward, pull back toward your body for 15s.",
            "4. Make gentle circles with both wrists and shake out your hands."
        ],
        "benefit": "Prevents median nerve compression and typing tendonitis."
    },
    {
        "title": "Shoulder Blade Retraction & Neck Release",
        "cat_art": "(=^ω^=) 🪶",
        "duration": "60 seconds",
        "steps": [
            "1. Sit tall. Pull both shoulder blades back and down as if pinching a pencil.",
            "2. Hold for 5 seconds, release. Repeat 4 times.",
            "3. Gently drop your right ear toward your right shoulder for 15s.",
            "4. Switch to the left side and breathe into the neck stretch."
        ],
        "benefit": "Counters forward-head posture and upper back tension."
    },
    {
        "title": "Standing Spine & Hamstring Unwind",
        "cat_art": "(=^ ◡ ^=) 🐾",
        "duration": "60 seconds",
        "steps": [
            "1. Stand up from your desk completely.",
            "2. Reach both arms high toward the ceiling and interlock fingers.",
            "3. Take a deep breath and arch gently backward.",
            "4. Bend forward gently toward your toes with soft knees, exhaling fully."
        ],
        "benefit": "Restores lumbar circulation and reactivates posterior chain blood flow."
    }
]

class StretchModal:
    def __init__(self, parent, theme_colors: dict, pet_name: str = "Neko", on_complete_callback=None):
        self.parent = parent
        self.colors = theme_colors
        self.pet_name = pet_name
        self.on_complete_callback = on_complete_callback
        self.current_index = 0

        self.window = tk.Toplevel(parent)
        self.window.title(f"{pet_name}'s Ergonomic Micro-Stretches")
        self.window.geometry("420x420")
        self.window.resizable(False, False)
        self.window.configure(bg=self.colors.get("bg_main", "#FFF5E4"))
        self.window.attributes("-topmost", True)

        self._center_window()
        self._build_ui()
        self._render_routine()

    def _center_window(self):
        self.window.update_idletasks()
        w = 420
        h = 420
        px = self.parent.winfo_rootx()
        py = self.parent.winfo_rooty()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        x = max(50, px + (pw // 2) - (w // 2))
        y = max(50, py + (ph // 2) - (h // 2))
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.window, bg=self.colors.get("header_bg", "#FF9494"), pady=8)
        hdr.pack(fill=tk.X)

        tk.Label(
            hdr,
            text=f"🐾  {self.pet_name}'s Physical Recharge Guide",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors.get("header_bg", "#FF9494"),
            fg="white"
        ).pack()

        # Content Container Card
        self.card = tk.Frame(self.window, bg=self.colors.get("bg_card", "#FFE3E1"), padx=15, pady=12)
        self.card.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # Cat Avatar / Icon
        self.lbl_art = tk.Label(
            self.card,
            text="",
            font=("Segoe UI", 16, "bold"),
            bg=self.colors.get("bg_card", "#FFE3E1"),
            fg=self.colors.get("accent", "#FF6B6B")
        )
        self.lbl_art.pack(pady=2)

        # Title
        self.lbl_routine_title = tk.Label(
            self.card,
            text="",
            font=("Segoe UI", 13, "bold"),
            bg=self.colors.get("bg_card", "#FFE3E1"),
            fg=self.colors.get("text_primary", "#2D3436")
        )
        self.lbl_routine_title.pack()

        # Duration
        self.lbl_duration = tk.Label(
            self.card,
            text="",
            font=("Segoe UI", 9, "italic"),
            bg=self.colors.get("bg_card", "#FFE3E1"),
            fg=self.colors.get("accent", "#FF6B6B")
        )
        self.lbl_duration.pack(pady=2)

        # Steps Text
        self.lbl_steps = tk.Label(
            self.card,
            text="",
            font=("Segoe UI", 9),
            bg=self.colors.get("bg_card", "#FFE3E1"),
            fg=self.colors.get("text_primary", "#2D3436"),
            justify=tk.LEFT,
            wraplength=350
        )
        self.lbl_steps.pack(pady=6)

        # Benefit
        self.lbl_benefit = tk.Label(
            self.card,
            text="",
            font=("Segoe UI", 8, "italic"),
            bg=self.colors.get("bg_card", "#FFE3E1"),
            fg=self.colors.get("text_secondary", "#636E72"),
            wraplength=350
        )
        self.lbl_benefit.pack(pady=2)

        # Navigation Bar
        nav_frame = tk.Frame(self.window, bg=self.colors.get("bg_main", "#FFF5E4"), pady=6)
        nav_frame.pack(fill=tk.X, padx=16)

        self.btn_prev = tk.Button(
            nav_frame,
            text="◀ Previous",
            font=("Segoe UI", 9),
            bg=self.colors.get("btn_secondary", "#FFE3E1"),
            fg=self.colors.get("text_primary", "#2D3436"),
            relief=tk.FLAT,
            padx=10,
            command=self._prev
        )
        self.btn_prev.pack(side=tk.LEFT)

        self.lbl_counter = tk.Label(
            nav_frame,
            text="1 / 4",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors.get("bg_main", "#FFF5E4"),
            fg=self.colors.get("text_secondary", "#636E72")
        )
        self.lbl_counter.pack(side=tk.LEFT, expand=True)

        self.btn_next = tk.Button(
            nav_frame,
            text="Next ▶",
            font=("Segoe UI", 9),
            bg=self.colors.get("btn_primary", "#FF9494"),
            fg="white",
            relief=tk.FLAT,
            padx=12,
            command=self._next
        )
        self.btn_next.pack(side=tk.RIGHT)

    def _render_routine(self):
        item = STRETCH_ROUTINES[self.current_index]
        self.lbl_art.config(text=item["cat_art"])
        self.lbl_routine_title.config(text=item["title"])
        self.lbl_duration.config(text=f"⏱ Recommended: {item['duration']}")
        self.lbl_steps.config(text="\n".join(item["steps"]))
        self.lbl_benefit.config(text=f"💡 Health Perk: {item['benefit']}")
        self.lbl_counter.config(text=f"{self.current_index + 1} of {len(STRETCH_ROUTINES)}")

        self.btn_prev.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        if self.current_index == len(STRETCH_ROUTINES) - 1:
            self.btn_next.config(text="Finished! ✨")
        else:
            self.btn_next.config(text="Next ▶")

    def _next(self):
        if self.current_index < len(STRETCH_ROUTINES) - 1:
            self.current_index += 1
            self._render_routine()
        else:
            if self.on_complete_callback:
                self.on_complete_callback()
            self.window.destroy()

    def _prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self._render_routine()
