"""
GrndworkOS — AI Routing Backend
Deploy this to Railway. Set CLAUDE_KEY and GEMINI_KEY as environment variables.
Never put real API keys in this file directly.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)

# Allow requests from your Netlify domain only
CORS(app, origins=[
    "https://grndworkos.com",
    "https://www.grndworkos.com",
    "https://grndworkos.netlify.app",
    "http://localhost:3000",   # for local development
])

CLAUDE_KEY = os.environ.get("CLAUDE_KEY", "")
GEMINI_KEY = os.environ.get("GEMINI_KEY", "")

# ─── TASK CLASSIFICATION ──────────────────────────────────────────────────────

SIMPLE_TASKS = [
    "Generate daily report", "Recap Cedar Valley", "Generate client progress report",
    "Add captions", "Create before/after", "Open full photo gallery",
    "Generate digital haul report", "Create new electronic haul ticket",
    "Archive all reconciled", "Find available carriers",
    "Contact Southwest Haul Brokers", "Message sent to all network",
    "Export inventory report", "Sync latest rental data",
    "Open Caterpillar rental portal",
]

MODERATE_TASKS = [
    "Create safety checklist", "Export payroll", "Run direct deposit",
    "Message Marco", "Dispatch next available", "Dispatch Walsh Trucking",
    "Dispatch Ruiz Hauling", "Send haul request", "Post new haul request",
    "Order material delivery", "Export full audit trail",
    "Log service request", "Schedule service", "Schedule return",
    "Confirm return", "Extend rental", "Connect Sunbelt", "Connect United",
    "Log usage hours", "Generate rental cost report",
    "Sync all rental invoices", "Accept Walsh Trucking bid",
    "Accept Summit Transport bid", "Accept Rocky Mountain Quarry",
]

PREMIUM_TASKS = [
    "Generate prevailing wage report", "Build new bid from historical data",
    "Reconcile haul ticket", "Review new aggregate quote",
    "View AZ Dirt Works subcontract",
]

SYSTEM_PROMPTS = {
    "gemini": "You are a field operations assistant inside GrndworkOS, a construction management platform. Be brief and practical. 2-3 sentences max.",
    "haiku":  "You are a field operations assistant inside GrndworkOS. Be accurate and structured. Keep responses under 4 sentences.",
    "sonnet": "You are a senior field operations analyst inside GrndworkOS. Think carefully. Flag any risks, compliance issues, or financial implications. Use clear sections if needed.",
}

def classify_task(action: str) -> str:
    if any(t in action for t in PREMIUM_TASKS):  return "sonnet"
    if any(t in action for t in MODERATE_TASKS): return "haiku"
    return "gemini"


# ─── API CALLERS ──────────────────────────────────────────────────────────────

def call_gemini(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
    data = res.json()
    if "error" in data:
        raise Exception(data["error"]["message"])
    return data["candidates"][0]["content"]["parts"][0]["text"]


def call_claude(prompt: str, model: str) -> str:
    model_id = "claude-sonnet-4-6" if model == "sonnet" else "claude-haiku-4-5-20251001"
    res = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "Content-Type": "application/json",
            "x-api-key": CLAUDE_KEY,
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": model_id,
            "max_tokens": 2048 if model == "sonnet" else 1024,
            "system": SYSTEM_PROMPTS[model],
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    data = res.json()
    if "error" in data:
        raise Exception(data["error"]["message"])
    return data["content"][0]["text"]


# ─── ROUTES ───────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "grndworkos-ai"})


@app.route("/ai", methods=["POST"])
def ai_action():
    body = request.get_json()
    if not body or "action" not in body:
        return jsonify({"error": "Missing 'action' field"}), 400

    action = body["action"]
    model  = classify_task(action)
    prompt = f"{SYSTEM_PROMPTS[model]}\n\nUser triggered: \"{action}\". Respond as a smart field operations assistant for a construction company."

    try:
        if model == "gemini":
            reply = call_gemini(prompt)
        else:
            reply = call_claude(prompt, model)

        return jsonify({
            "reply": reply,
            "model": model,
            "model_label": {"gemini": "Gemini Flash", "haiku": "Claude Haiku", "sonnet": "Claude Sonnet"}[model],
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
