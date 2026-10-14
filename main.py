"""
Entry point for AI Desktop Wellness Companion.
"""

import sys
import os
import tkinter as tk
from companion_app import DesktopWellnessCompanion

def enable_high_dpi_awareness():
    """Enable Windows high DPI scaling for crisp text and graphics."""
    if sys.platform == "win32":
        try:
            import ctypes
            # Try Per-Monitor V2 awareness (Windows 10 1703+)
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

def main():
    enable_high_dpi_awareness()
    root = tk.Tk()
    app = DesktopWellnessCompanion(root)
    root.mainloop()

if __name__ == "__main__":
    main()
