"""
Configuration Manager for AI Desktop Wellness Companion.
Handles persistent storage of user preferences and API credentials.
"""

import json
import os
from typing import Dict, Any

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG: Dict[str, Any] = {
    "api_key": "",
    "model_name": "gemini-2.5-flash",
    "pet_name": "Neko",
    "work_duration_minutes": 25,
    "break_duration_minutes": 5,
    "burnout_threshold_minutes": 50,
    "sound_enabled": True,
    "always_on_top": True,
    "theme": "pastel_peach",
    "daily_water_count": 0,
    "daily_stretch_count": 0,
    "daily_breathing_count": 0
}

COLOR_THEMES = {
    "pastel_peach": {
        "bg_main": "#FFF5E4",
        "bg_card": "#FFE3E1",
        "header_bg": "#FF9494",
        "accent": "#FF6B6B",
        "text_primary": "#2D3436",
        "text_secondary": "#636E72",
        "btn_primary": "#FF9494",
        "btn_secondary": "#FFE3E1",
        "progress_fill": "#FF6B6B",
        "progress_bg": "#F0E4D7",
        "highlight": "#FFD1D1"
    },
    "mint_calm": {
        "bg_main": "#E8F5E9",
        "bg_card": "#C8E6C9",
        "header_bg": "#81C784",
        "accent": "#4CAF50",
        "text_primary": "#1B5E20",
        "text_secondary": "#388E3C",
        "btn_primary": "#81C784",
        "btn_secondary": "#C8E6C9",
        "progress_fill": "#4CAF50",
        "progress_bg": "#D0E7D2",
        "highlight": "#A5D6A7"
    },
    "lavender_night": {
        "bg_main": "#F3E8FF",
        "bg_card": "#E9D5FF",
        "header_bg": "#C084FC",
        "accent": "#9333EA",
        "text_primary": "#3B0764",
        "text_secondary": "#6B21A8",
        "btn_primary": "#C084FC",
        "btn_secondary": "#E9D5FF",
        "progress_fill": "#9333EA",
        "progress_bg": "#E5D9F2",
        "highlight": "#D8B4FE"
    },
    "dark_slate": {
        "bg_main": "#1E1E2E",
        "bg_card": "#2A2A3E",
        "header_bg": "#3B3B54",
        "accent": "#F38BA8",
        "text_primary": "#CDD6F4",
        "text_secondary": "#BAC2DE",
        "btn_primary": "#F38BA8",
        "btn_secondary": "#45475A",
        "progress_fill": "#A6E3A1",
        "progress_bg": "#313244",
        "highlight": "#F5C2E7"
    }
}


def load_config() -> Dict[str, Any]:
    """Load configuration from disk, filling in missing defaults."""
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                config.update(saved)
        except Exception as e:
            print(f"[ConfigManager] Error reading config: {e}. Using defaults.")

    # Check environment variable if api_key not set in file
    env_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not config.get("api_key") and env_key:
        config["api_key"] = env_key

    return config


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to disk."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"[ConfigManager] Error saving config: {e}")
        return False
