"""
Unit and integration test suite for AI Desktop Wellness Companion.
"""

import unittest
import os
import time
from config_manager import load_config, save_config, DEFAULT_CONFIG
from burnout_detector import BurnoutDetector
from gemini_client import GeminiWellnessClient

class TestWellnessCompanion(unittest.TestCase):
    def test_config_manager(self):
        config = load_config()
        self.assertIn("pet_name", config)
        self.assertIn("work_duration_minutes", config)
        self.assertIn("theme", config)

    def test_burnout_detector_initial_state(self):
        detector = BurnoutDetector(work_duration_mins=25, break_duration_mins=5, burnout_threshold_mins=50)
        self.assertEqual(detector.current_state, "WORKING")
        metrics = detector.calculate_burnout_metrics()
        self.assertIn("score", metrics)
        self.assertIn("level", metrics)
        self.assertIn(metrics["level"], ["Low", "Moderate", "High"])

    def test_burnout_actions(self):
        detector = BurnoutDetector()
        initial_water = detector.water_count
        detector.log_action("water")
        self.assertEqual(detector.water_count, initial_water + 1)

        initial_stretch = detector.stretch_count
        detector.log_action("stretch")
        self.assertEqual(detector.stretch_count, initial_stretch + 1)

        initial_breath = detector.breathing_count
        detector.log_action("breathing")
        self.assertEqual(detector.breathing_count, initial_breath + 1)

    def test_burnout_work_break_cycle(self):
        detector = BurnoutDetector(work_duration_mins=25, break_duration_mins=5)
        self.assertEqual(detector.current_state, "WORKING")
        detector.start_break()
        self.assertEqual(detector.current_state, "BREAK")
        self.assertEqual(detector.breaks_taken, 1)
        detector.resume_work()
        self.assertEqual(detector.current_state, "WORKING")

    def test_gemini_client_offline_fallback(self):
        client = GeminiWellnessClient(api_key="", pet_name="Neko")
        self.assertFalse(client.has_api_key())

        context = {
            "elapsed_minutes": 35,
            "burnout_level": "Moderate",
            "burnout_score": 50,
            "time_of_day": "Afternoon",
            "water_count": 2
        }
        checkin_msg, is_live = client.generate_burnout_checkin(context)
        self.assertFalse(is_live)
        self.assertTrue(len(checkin_msg) > 5)

        # Chat sentiment fallback tests
        chat_reply, is_live = client.chat("I feel so stressed and overwhelmed with bugs", context)
        self.assertFalse(is_live)
        self.assertTrue("breath" in chat_reply.lower() or "purr" in chat_reply.lower() or "puzzle" in chat_reply.lower())

if __name__ == "__main__":
    unittest.main()
