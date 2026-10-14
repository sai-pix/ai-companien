"""
Gemini API Client and Smart Offline Fallback Engine for AI Desktop Wellness Companion.
Integrates with Google's Gemini models (gemini-2.5-flash / gemini-1.5-flash) to provide
dynamic, empathetic, context-aware burnout coaching and companion conversations.
"""

import json
import random
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.error

class GeminiWellnessClient:
    def __init__(self, api_key: str = "", model_name: str = "gemini-2.5-flash", pet_name: str = "Neko"):
        self.api_key = api_key.strip()
        self.model_name = model_name
        self.pet_name = pet_name
        self.conversation_history: List[Dict[str, str]] = []

    def set_api_key(self, api_key: str):
        self.api_key = api_key.strip()

    def set_pet_name(self, pet_name: str):
        self.pet_name = pet_name

    def has_api_key(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def _get_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        ctx_info = ""
        if context:
            ctx_info = (
                f"\nUser Current Context:\n"
                f"- Continuous Focus Time: {context.get('elapsed_minutes', 0)} mins\n"
                f"- Burnout Risk Level: {context.get('burnout_level', 'Low')} ({context.get('burnout_score', 0)}%)\n"
                f"- Time of Day: {context.get('time_of_day', 'Daytime')}\n"
                f"- Water Breaks today: {context.get('water_count', 0)}\n"
            )

        return (
            f"You are {self.pet_name}, an adorable, empathetic, caring AI desktop wellness companion cat. "
            f"You sit on the user's desktop to guard against burnout, eye strain, physical stiffness, and anxiety. "
            f"Keep your answers concise (1 to 3 warm sentences), helpful, and slightly feline (occasional cute 'meow', 'purr', '*gentle paw tap*'). "
            f"Offer actionable micro-habits: hydrate, stretch wrists/neck, deep breath, 20-20-20 rule, or mindset reframing. "
            f"Never sound clinical or scolding; always be uplifting and comforting.{ctx_info}"
        )

    def test_connection(self) -> tuple[bool, str]:
        """Verify if current API key is valid."""
        if not self.has_api_key():
            return False, "No API key configured."
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {"parts": [{"text": "Hello! Reply with 'Purr! Connected successfully.'"}]}
                ],
                "generationConfig": {
                    "maxOutputTokens": 30,
                    "temperature": 0.5
                }
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    return True, text.strip() or "Connected successfully!"
            return False, f"Unexpected response status: {response.status}"
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode("utf-8")
                err_json = json.loads(err_body)
                msg = err_json.get("error", {}).get("message", str(e))
            except Exception:
                msg = str(e)
            return False, f"API Error: {msg}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def generate_burnout_checkin(self, context: Dict[str, Any]) -> tuple[str, bool]:
        """
        Generate a dynamic wellness prompt based on session time and burnout score.
        Returns: (message_text, is_ai_live)
        """
        if self.has_api_key():
            prompt = (
                f"I noticed the user has been working continuously for {context.get('elapsed_minutes', 0)} minutes. "
                f"Their burnout risk indicator is currently {context.get('burnout_level', 'Low')} ({context.get('burnout_score', 0)}%). "
                f"Give them a delightful, cute cat check-in reminding them to take care of themselves."
            )
            ai_reply = self._call_gemini_single_prompt(prompt, context)
            if ai_reply:
                return ai_reply, True

        # Fallback smart local generator
        return self._generate_offline_checkin(context), False

    def chat(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> tuple[str, bool]:
        """
        Chat with the companion about feelings, stress, coding blocks, or request advice.
        Returns: (reply_text, is_ai_live)
        """
        if self.has_api_key():
            prompt = f"User says to you: '{user_message}'\nRespond in your persona as {self.pet_name}."
            ai_reply = self._call_gemini_single_prompt(prompt, context)
            if ai_reply:
                return ai_reply, True

        # Offline fallback smart engine
        return self._generate_offline_chat(user_message, context), False

    def _call_gemini_single_prompt(self, user_prompt: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Call Gemini REST API with system instruction."""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            system_instruction = self._get_system_prompt(context)
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"[System Persona Instructions]\n{system_instruction}\n\n[Task]\n{user_prompt}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 150
                }
            }
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                if response.status == 200:
                    resp_json = json.loads(response.read().decode("utf-8"))
                    text = (
                        resp_json.get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "")
                    )
                    if text:
                        return text.strip()
        except Exception as e:
            print(f"[GeminiClient] Fallback triggered due to API issue: {e}")
        return None

    def _generate_offline_checkin(self, context: Dict[str, Any]) -> str:
        """Rule-based smart response when offline or key not provided."""
        elapsed = context.get("elapsed_minutes", 0)
        level = context.get("burnout_level", "Low")
        hour = datetime.now().hour

        is_late_night = hour >= 23 or hour < 5
        is_evening = 18 <= hour < 23

        if is_late_night:
            return random.choice([
                f"*meows softly from your desk* It's past midnight! Your brain worked hard today. Time to tuck in soon? Purr...",
                f"(=^..^=) Late night coding? Even nocturnal cats need sleep. Drink some chamomile or warm water!",
                f"Meow... Late-night screen glow strains your pretty eyes. Rest is where the best solutions crystallize!"
            ])

        if level == "High" or elapsed >= 50:
            return random.choice([
                f"*places a gentle paw on your mouse* Meow! You've been focusing for {elapsed} mins straight! Roll your shoulders back and take a 5-minute stroll.",
                f"(=^o^=) High focus detected! Your brain is heating up. Look out a window for 20 seconds and drink some water!",
                f"Purrrr... Cat emergency! You deserve a quick break. Stretch those typing claws and take 3 deep belly breaths."
            ])
        elif level == "Moderate" or elapsed >= 25:
            return random.choice([
                f"Meow! 25 minutes of steady work completed! Unclench your jaw and rest your eyes for a brief moment.",
                f"(=^ ◡ ^=) *purr* Halfway through a solid focus sprint. Remember the 20-20-20 rule: look 20 feet away for 20 seconds!",
                f"Hydration check! Have you had water recently? *nudges water glass with paw*"
            ])
        else:
            return random.choice([
                f"(=^ ◡ ^=) Purring quietly beside you. You're doing great, take it one step at a time!",
                f"Meow! Fresh focus session started. Keep your posture tall and your spirits light!",
                f"*happy cat tail wag* I'm right here cheering for your productivity today!"
            ])

    def _generate_offline_chat(self, user_msg: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Sentiment-aware offline companion conversation."""
        msg_lower = user_msg.lower()

        # Anxiety / Stress / Overwhelm
        if any(w in msg_lower for w in ["stress", "anxious", "anxiety", "overwhelm", "panic", "scared", "nervous"]):
            return random.choice([
                f"(=^..^=) *slow blinks at you with affection* Take a slow, deep breath with me. Inhale for 4 seconds... exhale for 4. You don't have to solve everything this very second.",
                f"*gently curls into your lap* I hear you. When things feel overwhelming, pick just one tiny puzzle piece to tackle. You've got this, purr...",
                f"Meow... I can feel the tension. Try our Guided Breathing exercise from the menu right now. Just 1 minute will help calm your nervous system!"
            ])

        # Exhaustion / Tired / Burnout / Sleepy
        if any(w in msg_lower for w in ["tired", "exhaust", "sleepy", "burnout", "drained", "no energy", "fatigue"]):
            return random.choice([
                f"(=^o^=) *yawn* Your brain energy meter is running low! Can you step away for 5 minutes, stretch, and grab a fresh glass of water?",
                f"Purr... Working when drained takes twice the effort. Even a 3-minute screen break helps reboot your cognitive battery!",
                f"Meow! Rest is productive too. If it's been a long grind, give yourself permission to step away without guilt."
            ])

        # Stuck / Bug / Frustrated / Angry / Error
        if any(w in msg_lower for w in ["stuck", "bug", "error", "hate", "angry", "frustrat", "fail", "broken", "annoy"]):
            return random.choice([
                f"(=^ω^=) Ah, the dreaded stubborn bug! Rubber duck debugging works, but rubber *cat* debugging is purr-fection. Walk away for 3 minutes, then look with fresh eyes!",
                f"*swats the invisible bug away* Frustration is just your brain trying to build a new connection. Shake out your hands, roll your neck, and take a sip of water.",
                f"Meow! Hard problems are tough. Be kind to yourself! Sometimes the best eureka moment happens when you stand up and stretch."
            ])

        # Happy / Productive / Good / Done
        if any(w in msg_lower for w in ["good", "great", "happy", "done", "fixed", "yay", "awesome", "proud", "solved"]):
            return random.choice([
                f"(=^ ◡ ^=) *triumphant purr and high paw!* That's wonderful! Celebrate your win—you earned it!",
                f"Meow yay! Look at you conquering your goals! Keep this gentle, positive momentum going.",
                f"*rubs cheeks against your screen happily* Purrrrr! A happy human makes for a happy companion!"
            ])

        # Breathing / Meditation request
        if any(w in msg_lower for w in ["breath", "meditat", "calm", "relax"]):
            return "(=^ ◡ ^=) Click the 'Guided Breathing' button below! I'll guide you through soothing Box Breathing to re-center your mind."

        # Water / Hydration
        if any(w in msg_lower for w in ["water", "thirst", "drink", "tea", "coffee"]):
            return "(=^..^=) Cheers! Hydration keeps your brain cells firing fast. Click the '+Water' button to log your drink!"

        # Default supportive response
        return random.choice([
            f"(=^ ◡ ^=) *purrs warmly* I'm right here with you! Tell me how your focus is feeling, or click 'Breathe' for a peaceful pause.",
            f"Meow! Remember: posture check! Drop your shoulders away from your ears and soften your brow.",
            f"(=^ω^=) Keeping you company through your tasks. You're doing wonderful work today, human!"
        ])
