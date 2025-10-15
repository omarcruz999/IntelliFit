# IntelliFit — AI Workout Generator 💪
IntelliFit is an AI-powered workout planner that creates personalized routines based on your fitness level, goals, and restrictions. It adapts to your progress, offering safe, effective, and flexible workouts—helping you stay consistent and reach your goals anywhere, anytime.

## ✨ What it does

* 🧭 Takes your inputs (**Beginner/Intermediate/Advanced**, **Weight Loss/Muscle/Maintenance**, **Restrictions**).
* 🧠 Sends a structured prompt to **Gemini**.
* 📦 Returns **valid JSON** and renders a polished workout in the browser.

---

## 🚀 Quick Start

### 1) Install

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install Flask python-dotenv google-genai
```

### 2) Set your API key 🔐

Create a `.env` (where `load_dotenv()` reads it) and add:

```
GEMINI_API_KEY=your_api_key_here
```

### 3) Confirm template path 🗂️

### 4) Run ▶️

```bash
python app.py
```

Open: **[http://localhost:5002](http://localhost:5002)**

---

## 🖥️ Use the App

1. 🧱 Pick **Skill Level**
2. 🎯 Pick **Workout Goal**
3. 🚧 Enter **Restrictions** (e.g., `no equipment, limited time`)
4. ⚡ Click **Generate Workout**

You’ll see a formatted plan plus the details (warm-up, main sets, finisher, tips).

---

## 🔌 API (Optional)

**Endpoint**

```
POST /generate_workout
```

**Body**

```json
{
  "skill_level": "beginner",
  "workout_goal": "weight loss",
  "restrictions": "no equipment, limited time"
}
```

**cURL**

```bash
curl -X POST http://localhost:5002/generate_workout \
  -H "Content-Type: application/json" \
  -d '{"skill_level":"intermediate","workout_goal":"muscle building","restrictions":"dumbbells only"}'
```

---

## 🛠️ Troubleshooting

* ❌ **Auth error**: Check `GEMINI_API_KEY` and that `.env` is loaded.
* 📄 **Template not found**: Fix the `template.txt` path in `app.py`.
* 🧩 **JSON parse issues**: Keep the prompt strict: “**Output only valid JSON. No markdown.**”

---

## 📜 License

MIT — use and modify freely.
