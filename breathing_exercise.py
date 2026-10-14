"""
Guided Box Breathing Exercise for AI Desktop Wellness Companion.
Provides an animated expanding/contracting circle modal for instant stress relief.
"""

import tkinter as tk
import math

class BreathingModal:
    def __init__(self, parent, theme_colors: dict, pet_name: str = "Neko", on_complete_callback=None):
        self.parent = parent
        self.colors = theme_colors
        self.pet_name = pet_name
        self.on_complete_callback = on_complete_callback

        self.window = tk.Toplevel(parent)
        self.window.title(f"{pet_name}'s Guided Breathing Sanctuary")
        self.window.geometry("380x420")
        self.window.resizable(False, False)
        self.window.configure(bg=self.colors.get("bg_main", "#FFF5E4"))
        self.window.attributes("-topmost", True)

        # Center on parent or screen
        self.center_window()

        # Breathing cycle state
        # 4 phases: Inhale (4s), Hold (4s), Exhale (4s), Rest (4s)
        self.phases = [
            {"name": "Inhale deeply...", "instruction": "Breathe in through your nose, expand your belly", "duration": 4.0, "mode": "expand"},
            {"name": "Hold gently...", "instruction": "Keep your breath steady and relaxed", "duration": 4.0, "mode": "hold_in"},
            {"name": "Exhale slowly...", "instruction": "Release all stress through your mouth", "duration": 4.0, "mode": "contract"},
            {"name": "Hold & Rest...", "instruction": "Notice the quiet stillness inside", "duration": 4.0, "mode": "hold_out"},
        ]
        self.total_cycles = 3
        self.current_cycle = 1
        self.current_phase_idx = 0
        self.step_interval_ms = 40  # ~25 fps animation
        self.elapsed_in_phase_ms = 0
        self.is_running = True

        self.min_radius = 45
        self.max_radius = 110
        self.current_radius = self.min_radius

        self._build_ui()
        self._animate_step()

    def center_window(self):
        self.window.update_idletasks()
        w = 380
        h = 420
        px = self.parent.winfo_rootx()
        py = self.parent.winfo_rooty()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        x = max(50, px + (pw // 2) - (w // 2))
        y = max(50, py + (ph // 2) - (h // 2))
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # Header title
        title_frame = tk.Frame(self.window, bg=self.colors.get("header_bg", "#FF9494"), pady=8)
        title_frame.pack(fill=tk.X)

        lbl_title = tk.Label(
            title_frame,
            text=f"(=^ ◡ ^=)  {self.pet_name}'s Calming Breath",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors.get("header_bg", "#FF9494"),
            fg="white"
        )
        lbl_title.pack()

        # Canvas for animated expanding/contracting breathing orb
        self.canvas = tk.Canvas(
            self.window,
            width=300,
            height=230,
            bg=self.colors.get("bg_main", "#FFF5E4"),
            highlightthickness=0
        )
        self.canvas.pack(pady=10)

        # Labels for phase instruction and cycle counter
        self.lbl_phase = tk.Label(
            self.window,
            text="Inhale deeply...",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors.get("bg_main", "#FFF5E4"),
            fg=self.colors.get("text_primary", "#2D3436")
        )
        self.lbl_phase.pack()

        self.lbl_instruction = tk.Label(
            self.window,
            text="Breathe in through your nose, expand your belly",
            font=("Segoe UI", 9),
            bg=self.colors.get("bg_main", "#FFF5E4"),
            fg=self.colors.get("text_secondary", "#636E72"),
            wraplength=340
        )
        self.lbl_instruction.pack(pady=4)

        self.lbl_cycle = tk.Label(
            self.window,
            text=f"Cycle {self.current_cycle} of {self.total_cycles}",
            font=("Segoe UI", 9, "italic"),
            bg=self.colors.get("bg_main", "#FFF5E4"),
            fg=self.colors.get("accent", "#FF6B6B")
        )
        self.lbl_cycle.pack(pady=2)

        # Bottom Close button
        btn_frame = tk.Frame(self.window, bg=self.colors.get("bg_main", "#FFF5E4"))
        btn_frame.pack(pady=10)

        self.btn_done = tk.Button(
            btn_frame,
            text="Complete Session",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors.get("btn_primary", "#FF9494"),
            fg="white",
            relief=tk.FLAT,
            padx=16,
            pady=4,
            cursor="hand2",
            command=self._on_close
        )
        self.btn_done.pack()

        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _animate_step(self):
        if not self.is_running:
            return

        phase = self.phases[self.current_phase_idx]
        total_phase_ms = int(phase["duration"] * 1000)
        self.elapsed_in_phase_ms += self.step_interval_ms

        progress = min(1.0, self.elapsed_in_phase_ms / total_phase_ms)

        # Compute radius based on phase mode
        if phase["mode"] == "expand":
            # Smooth ease in-out
            factor = (1.0 - math.cos(progress * math.pi)) / 2.0
            self.current_radius = self.min_radius + (self.max_radius - self.min_radius) * factor
        elif phase["mode"] == "contract":
            factor = (1.0 - math.cos(progress * math.pi)) / 2.0
            self.current_radius = self.max_radius - (self.max_radius - self.min_radius) * factor
        elif phase["mode"] == "hold_in":
            # Gentle subtle breath ripple
            self.current_radius = self.max_radius + math.sin(progress * math.pi * 2) * 3
        else:  # hold_out
            self.current_radius = self.min_radius + math.sin(progress * math.pi * 2) * 2

        self._draw_circle()

        if self.elapsed_in_phase_ms >= total_phase_ms:
            # Advance to next phase
            self.elapsed_in_phase_ms = 0
            self.current_phase_idx += 1
            if self.current_phase_idx >= len(self.phases):
                self.current_phase_idx = 0
                self.current_cycle += 1
                if self.current_cycle > self.total_cycles:
                    self._show_finished()
                    return

            next_phase = self.phases[self.current_phase_idx]
            self.lbl_phase.config(text=next_phase["name"])
            self.lbl_instruction.config(text=next_phase["instruction"])
            self.lbl_cycle.config(text=f"Cycle {self.current_cycle} of {self.total_cycles}")

        self.window.after(self.step_interval_ms, self._animate_step)

    def _draw_circle(self):
        self.canvas.delete("all")
        cx = 150
        cy = 115
        r = self.current_radius

        # Outer soft aura rings
        accent_color = self.colors.get("accent", "#FF6B6B")
        card_color = self.colors.get("bg_card", "#FFE3E1")

        # Outer aura
        self.canvas.create_oval(
            cx - r - 15, cy - r - 15,
            cx + r + 15, cy + r + 15,
            fill=card_color,
            outline=""
        )

        # Core breathing sphere
        self.canvas.create_oval(
            cx - r, cy - r,
            cx + r, cy + r,
            fill=accent_color,
            outline="white",
            width=3
        )

        # Center cat emoji / icon
        phase = self.phases[self.current_phase_idx]
        face = "(=^ ◡ ^=)" if phase["mode"] in ["hold_in", "hold_out"] else "(=^..^=)"
        self.canvas.create_text(
            cx, cy,
            text=face,
            font=("Segoe UI", 13, "bold"),
            fill="white"
        )

    def _show_finished(self):
        self.is_running = False
        self.canvas.delete("all")
        self.canvas.create_text(
            150, 115,
            text="✨ (=^ω^=) ✨\n\nPurr-fect!\nYour nervous system is reset.",
            font=("Segoe UI", 13, "bold"),
            fill=self.colors.get("accent", "#FF6B6B"),
            justify="center"
        )
        self.lbl_phase.config(text="Session Complete!")
        self.lbl_instruction.config(text="Take this calm energy back into your day.")
        self.lbl_cycle.config(text="3 of 3 cycles completed")
        self.btn_done.config(text="Return to Companion ✨")

        if self.on_complete_callback:
            self.on_complete_callback()

    def _on_close(self):
        self.is_running = False
        if self.on_complete_callback and not self.is_running:
            self.on_complete_callback()
        self.window.destroy()
