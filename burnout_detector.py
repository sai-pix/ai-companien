"""
Burnout and Fatigue Detection Engine for AI Desktop Wellness Companion.
Tracks active work sessions, assesses fatigue risk score, and signals break recommendations.
"""

import time
from datetime import datetime
from typing import Dict, Any

class BurnoutDetector:
    def __init__(self, work_duration_mins: int = 25, break_duration_mins: int = 5, burnout_threshold_mins: int = 50):
        self.work_threshold_seconds = work_duration_mins * 60
        self.break_duration_seconds = break_duration_mins * 60
        self.burnout_threshold_seconds = burnout_threshold_mins * 60

        self.current_state = "WORKING"  # "WORKING" or "BREAK"
        self.session_start_time = time.time()
        self.break_start_time = 0.0

        self.total_focus_seconds_today = 0
        self.completed_sprints = 0
        self.breaks_taken = 0
        self.recent_sentiment_score = 0.0  # -1.0 (stressed/tired) to +1.0 (happy/calm)

        # Activity counters
        self.water_count = 0
        self.stretch_count = 0
        self.breathing_count = 0

    def set_durations(self, work_mins: int, break_mins: int, burnout_mins: int):
        self.work_threshold_seconds = max(1, work_mins) * 60
        self.break_duration_seconds = max(1, break_mins) * 60
        self.burnout_threshold_seconds = max(1, burnout_mins) * 60

    def get_elapsed_seconds(self) -> int:
        if self.current_state == "WORKING":
            return int(time.time() - self.session_start_time)
        else:
            return int(time.time() - self.break_start_time)

    def is_work_time_up(self) -> bool:
        return self.current_state == "WORKING" and self.get_elapsed_seconds() >= self.work_threshold_seconds

    def is_break_time_up(self) -> bool:
        return self.current_state == "BREAK" and self.get_elapsed_seconds() >= self.break_duration_seconds

    def start_break(self):
        if self.current_state == "WORKING":
            self.total_focus_seconds_today += self.get_elapsed_seconds()
            self.completed_sprints += 1
        self.current_state = "BREAK"
        self.break_start_time = time.time()
        self.breaks_taken += 1

    def resume_work(self):
        self.current_state = "WORKING"
        self.session_start_time = time.time()

    def reset_timer(self):
        if self.current_state == "WORKING":
            self.session_start_time = time.time()
        else:
            self.break_start_time = time.time()

    def record_sentiment(self, sentiment_score: float):
        """Update recent user sentiment (-1.0 to +1.0)."""
        self.recent_sentiment_score = max(-1.0, min(1.0, sentiment_score))

    def log_action(self, action_type: str):
        if action_type == "water":
            self.water_count += 1
        elif action_type == "stretch":
            self.stretch_count += 1
        elif action_type == "breathing":
            self.breathing_count += 1

    def calculate_burnout_metrics(self) -> Dict[str, Any]:
        """
        Calculates holistic burnout risk score (0 to 100%) based on:
        - Continuous unbroken focus duration
        - Time of day (late-night overwork penalty)
        - Deficit of breaks/hydration
        - Mood sentiment feedback
        """
        elapsed_mins = self.get_elapsed_seconds() / 60.0 if self.current_state == "WORKING" else 0.0

        # Base score from continuous focus time (0 - 60 points)
        # 0-25 mins -> 0-30 pts, 25-50 mins -> 30-55 pts, >50 mins -> 55-60+ pts
        if elapsed_mins <= 25:
            base_score = (elapsed_mins / 25.0) * 30.0
        elif elapsed_mins <= 50:
            base_score = 30.0 + ((elapsed_mins - 25.0) / 25.0) * 25.0
        else:
            base_score = 55.0 + min(20.0, ((elapsed_mins - 50.0) / 40.0) * 20.0)

        # Late-night work penalty (+15 points if 11 PM to 5 AM)
        now_hour = datetime.now().hour
        late_night_penalty = 15.0 if (now_hour >= 23 or now_hour < 5) else (5.0 if now_hour >= 21 else 0.0)

        # Sentiment penalty/bonus (-10 to +15 points)
        sentiment_penalty = 0.0
        if self.recent_sentiment_score < 0:
            sentiment_penalty = abs(self.recent_sentiment_score) * 15.0
        else:
            sentiment_penalty = - (self.recent_sentiment_score * 10.0)

        # Hydration / wellness bonus
        wellness_bonus = min(15.0, (self.water_count * 2.0 + self.stretch_count * 3.0 + self.breathing_count * 4.0))

        raw_score = base_score + late_night_penalty + sentiment_penalty - wellness_bonus
        final_score = int(max(5, min(100, raw_score)))

        if final_score < 35:
            level = "Low"
            status_desc = "Fresh & Alert"
            color = "#2ECC71"  # Fresh green
            recommendation = "You're in a great focus zone! Keep your posture relaxed."
        elif final_score < 65:
            level = "Moderate"
            status_desc = "Mild Fatigue"
            color = "#F39C12"  # Amber orange
            recommendation = "Fatigue is building up. Drink water or blink 20 times."
        else:
            level = "High"
            status_desc = "Burnout Risk"
            color = "#E74C3C"  # Coral red
            recommendation = "High cognitive fatigue! Step away for a short guided break."

        # Time of day string
        if 5 <= now_hour < 12:
            time_of_day = "Morning"
        elif 12 <= now_hour < 17:
            time_of_day = "Afternoon"
        elif 17 <= now_hour < 22:
            time_of_day = "Evening"
        else:
            time_of_day = "Late Night"

        return {
            "score": final_score,
            "level": level,
            "status_desc": status_desc,
            "color": color,
            "recommendation": recommendation,
            "elapsed_minutes": int(elapsed_mins),
            "state": self.current_state,
            "time_of_day": time_of_day,
            "water_count": self.water_count,
            "stretch_count": self.stretch_count,
            "breathing_count": self.breathing_count,
            "completed_sprints": self.completed_sprints
        }
