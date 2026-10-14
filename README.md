# 🐾 AI Desktop Wellness Companion (`Neko-Wellness`)

An interactive, AI-driven floating desktop companion engineered to combat **burnout, anxiety, eye strain, and digital fatigue** among students, developers, and remote workers.

Sitting unobtrusively in the corner of your screen, your companion keeps track of your focus sprints, dynamically computes cognitive fatigue and burnout risk, and provides context-aware guidance powered by **Google Gemini AI**.

---

## 🌟 Key Features

### 1. 🤖 Dynamic Gemini AI Integration
- Connects directly to Google's Gemini models (`gemini-2.5-flash` / `gemini-1.5-flash`).
- Employs a warm, empathetic feline persona designed to reduce cortisol, encourage deep breathing, and provide micro-wellness interventions.
- Context-aware coaching: considers your continuous focus time, burnout score, time of day (late-night warnings), and hydration levels.
- **Smart Local Mode**: Fully functional offline fallback engine with keyword sentiment analysis if no API key is provided or when offline.

### 2. ⚡ Intelligent Burnout & Fatigue Detection
- **Continuous Focus Tracker**: Tracks uninterrupted screen sessions with Pomodoro or custom time intervals.
- **Dynamic Burnout Risk Meter**: A live progress bar calculated from continuous work duration, late-night hours (11 PM - 5 AM penalty), hydration count, and user sentiment.
- **Automated Wellness Interventions**: Gentle chime and prompts when high burnout or session limits are detected.

### 3. 🌬️ Interactive Guided Box Breathing Sanctuary
- Dedicated animated visual modal featuring **Box Breathing** (4s Inhale, 4s Hold, 4s Exhale, 4s Rest).
- Smooth expanding/contracting visual orb with soothing instructions to lower heart rate and calm the autonomic nervous system.

### 4. 🤸 Ergonomic Micro-Stretching & 20-20-20 Eye Reset
- Step-by-step visual routines for desk-bound fatigue:
  - **20-20-20 Eye Reset**: Relieves digital eye strain and dry eye symptoms.
  - **Wrist & Finger Decompression**: Prevents carpal tunnel syndrome and RSI.
  - **Shoulder Blade & Neck Release**: Counters forward-head posture and slouching.
  - **Standing Spine Unwind**: Restores blood flow and lumbar posture.

### 5. 💧 Hydration & Wellness Streak Tracker
- Quick-log hydration (+Water counter).
- Each drink, stretch, and breathing cycle lowers your active burnout risk score!

### 6. 🎨 Delightful Desktop Experience
- **Frameless & Floating**: Sits above your work (`-topmost`) without window clutter.
- **Freely Draggable**: Click and drag from the header bar anywhere on screen.
- **Compact & Expanded Modes**: Collapse into a miniature desk pet badge (`▲` / `▼`) when you need extra screen space.
- **Theming**: Choose between `pastel_peach`, `mint_calm`, `lavender_night`, and `dark_slate`.

---

## 🚀 How to Run

### Method 1: Double-click Launcher
Double-click `run.bat` located inside the project folder:
```
C:\Users\kuran\.gemini\antigravity\scratch\wellness-companion\run.bat
```

### Method 2: From Terminal
```powershell
cd C:\Users\kuran\.gemini\antigravity\scratch\wellness-companion
python main.py
```

### Method 3: Running Tests
```powershell
python test_companion.py
```

---

## ⚙️ Configuring Gemini API Key

1. Click the **⚙️ (Settings)** icon on the companion widget.
2. Paste your Gemini API key in the key field (or set environment variable `GEMINI_API_KEY`).
3. Click **Test API Connection** to verify.
4. Click **Save & Apply**. The status badge will switch to **🟢 Gemini AI Live**!
*(If no key is entered, the app continues in **🟣 Smart Local Mode** without limitations).*

---

## 📂 Project Architecture

```
wellness-companion/
├── main.py               # Application entry point with Windows High-DPI support
├── companion_app.py      # Core floating desktop companion UI & animation loops
├── gemini_client.py      # Google Gemini API client + Smart Local fallback engine
├── burnout_detector.py   # Fatigue & burnout risk calculation engine
├── breathing_exercise.py # Animated Box Breathing modal canvas
├── stretch_guide.py      # Ergonomic micro-stretches and eye relaxation guide
├── settings_dialog.py    # Preferences dialog (API key, intervals, themes)
├── config_manager.py     # Persistent configuration & color themes
├── test_companion.py     # Unit test suite
└── run.bat               # Windows quick-launch script
```
