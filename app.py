"""
app.py

Flask backend for the Cloud Assistant chatbot.
Uses the Gemini API to generate responses restricted to the chatbot's topic,
as defined in chatbot_config.py.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

from chatbot_config import CHATBOT_TITLE, SYSTEM_PROMPT

# Load environment variables from .env
load_dotenv()

# ---- Configuration ----
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")
FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Add it to your .env file before running the app."
    )

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    system_instruction=SYSTEM_PROMPT,
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", chatbot_title=CHATBOT_TITLE)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    try:
        response = model.generate_content(user_message)
        reply_text = response.text.strip()
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"Failed to get a response: {exc}"}), 500

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=True)
