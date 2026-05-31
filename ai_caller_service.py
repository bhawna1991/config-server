import os
import json
import uuid
import time
import asyncio
import threading
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("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", "")
groq_client = Groq(api_keny=GROQ_API_KEY) if GROQ_API_KEY else None

active_calls = {}
call_reports = {}

COMPANY_PROFILE = {
    "name": "Mantaray AI",
    "product": "AI Agent Dashboard for lead management and customer engagement",
    "use_cases": ["Lead qualification", "Customer follow-up", "Campaign automation"],
    "target_segments": ["SMBs", "Enterprise sales teams", "CRM users"],
}

QUALIFICATION_QUESTIONS = [
    "Hello! I'm calling from {company}. Am I speaking with {lead_name}?",
    "Great! I wanted to quickly learn about your current lead management challenges. How are you currently handling lead follow-ups?",
    "Interesting. On a scale of 1 to 10, how satisfied are you with your current CRM setup?",
    "How many leads does your team handle per month roughly?",
    "Are you open to AI-powered automation to increase your team's productivity?",
    "What would be your ideal budget range for a solution like this?",
    "What's the best way and time to follow up with you?",
]

def build_system_prompt(lead_name, company_name):
    return f"""You are an AI sales agent calling on behalf of {COMPANY_PROFILE['name']}.
You are speaking with {lead_name} from {company_name}.
Your product is: {COMPANY_PROFILE['product']}.
Your goal is to qualify the lead by asking questions naturally, listening, and responding empathetically.
Keep your responses SHORT (1–2 sentences max). Be professional, friendly, and conversational.
After you have gathered enough info (5–6 exchanges), politely close the call and say goodbye.
Extract and remember: interest level, budget, current tool, pain points, follow-up preference."""


def generate_ai_response(call_id, user_message):
    call = active_calls.get(call_id)
    if not call:
        return "Call session not found."

    call["conversation"].append({"role": "user", "content": user_message})

    if not groq_client:
        response_text = f"Thank you for sharing that, {call['lead_name']}. We'll follow up shortly."
        call["conversation"].append({"role": "assistant", "content": response_text})
        return response_text

    messages = [{"role": "system", "content": call["system_prompt"]}] + call["conversation"]

    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        max_tokens=150,
        temperature=0.7,
    )
    ai_text = response.choices[0].message.content.strip()
    call["conversation"].append({"role": "assistant", "content": ai_text})
    return ai_text


def generate_call_report(call_id):
    call = active_calls.get(call_id)
    if not call:
        return {}

    conversation_text = "\n".join(
        [f"{'AI' if m['role'] == 'assistant' else 'Lead'}: {m['content']}" for m in call["conversation"]]
    )

    report_prompt = f"""You analyzed this sales call transcript between an AI agent and a lead.

Transcript:
{conversation_text}

Generate a JSON report with these exact keys:
- summary: 2-3 sentence summary of the call
- interestLevel: one of [High, Medium, Low]
- painPoints: list of strings (max 3)
- budget: string (extracted budget or "Not mentioned")
- currentTool: string (their current CRM/tool or "Not mentioned")
- followUpPreference: string
- qualificationScore: integer 1-10
- recommendedAction: string (next step)
- keyInsights: list of strings (max 3)

Respond with ONLY valid JSON."""

    if groq_client:
        try:
            resp = groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": report_prompt}],
                max_tokens=600,
                temperature=0.3,
            )
            raw = resp.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            report_data = json.loads(raw)
        except Exception:
            report_data = _fallback_report(call)
    else:
        report_data = _fallback_report(call)

    report = {
        "callId": call_id,
        "leadId": call.get("lead_id"),
        "leadName": call.get("lead_name"),
        "companyName": call.get("company_name"),
        "phone": call.get("phone"),
        "startTime": call.get("start_time"),
        "endTime": datetime.utcnow().isoformat(),
        "duration": int(time.time() - call.get("start_ts", time.time())),
        "status": "Completed",
        "conversation": call["conversation"],
        **report_data,
    }
    call_reports[call_id] = report
    return report


def _fallback_report(call):
    return {
        "summary": f"AI agent spoke with {call.get('lead_name')} from {call.get('company_name')}. Basic qualification questions were asked.",
        "interestLevel": "Medium",
        "painPoints": ["Lead management inefficiency"],
        "budget": "Not mentioned",
        "currentTool": "Not mentioned",
        "followUpPreference": "Email",
        "qualificationScore": 5,
        "recommendedAction": "Schedule a product demo",
        "keyInsights": ["Lead engaged with the call", "Open to follow-up"],
    }


@app.route("/api/ai-call/initiate", methods=["POST"])
def initiate_call():
    data = request.json
    lead_id = data.get("leadId")
    lead_name = data.get("leadName", "there")
    company_name = data.get("companyName", "your company")
    phone = data.get("phone", "")

    call_id = str(uuid.uuid4())
    opening_message = f"Hello! I'm an AI assistant calling from {COMPANY_PROFILE['name']}. May I speak with {lead_name} from {company_name}?"

    active_calls[call_id] = {
        "lead_id": lead_id,
        "lead_name": lead_name,
        "company_name": company_name,
        "phone": phone,
        "start_time": datetime.utcnow().isoformat(),
        "start_ts": time.time(),
        "system_prompt": build_system_prompt(lead_name, company_name),
        "conversation": [{"role": "assistant", "content": opening_message}],
        "status": "active",
        "question_index": 0,
    }

    return jsonify({
        "callId": call_id,
        "status": "initiated",
        "message": opening_message,
        "leadId": lead_id,
    })


@app.route("/api/ai-call/respond/<call_id>", methods=["POST"])
def respond_to_call(call_id):
    if call_id not in active_calls:
        return jsonify({"error": "Call not found"}), 404

    data = request.json
    user_message = data.get("message", "")

    ai_response = generate_ai_response(call_id, user_message)
    conversation_length = len(active_calls[call_id]["conversation"])

    should_end = (
        conversation_length >= 14
        or any(word in user_message.lower() for word in ["bye", "goodbye", "hang up", "end call", "not interested"])
        or any(word in ai_response.lower() for word in ["goodbye", "have a great day", "thank you for your time"])
    )

    return jsonify({
        "callId": call_id,
        "response": ai_response,
        "shouldEnd": should_end,
        "exchangeCount": conversation_length // 2,
    })


@app.route("/api/ai-call/end/<call_id>", methods=["POST"])
def end_call(call_id):
    if call_id not in active_calls:
        return jsonify({"error": "Call not found"}), 404

    active_calls[call_id]["status"] = "ended"
    report = generate_call_report(call_id)

    return jsonify({
        "callId": call_id,
        "status": "ended",
        "report": report,
    })


@app.route("/api/ai-call/report/<call_id>", methods=["GET"])
def get_report(call_id):
    report = call_reports.get(call_id)
    if not report:
        return jsonify({"error": "Report not found"}), 404
    return jsonify(report)


@app.route("/api/ai-call/simulate/<call_id>", methods=["POST"])
def simulate_full_call(call_id):
    if call_id not in active_calls:
        return jsonify({"error": "Call not found"}), 404

    call = active_calls[call_id]
    lead_name = call["lead_name"]

    simulated_responses = [
        f"Yes, this is {lead_name} speaking.",
        "We mostly use spreadsheets and manual email follow-ups. It's quite time consuming.",
        "I'd say around a 5 out of 10. We struggle with tracking.",
        "We handle about 200 leads per month.",
        "Yes, definitely open to trying something smarter.",
        "Budget would be around $500 to $1000 per month.",
        "Email works best. Mornings are good for me.",
    ]

    for user_msg in simulated_responses:
        generate_ai_response(call_id, user_msg)
        call_length = len(active_calls[call_id]["conversation"])
        if call_length >= 14:
            break

    active_calls[call_id]["status"] = "ended"
    report = generate_call_report(call_id)
    return jsonify({"callId": call_id, "status": "simulated", "report": report})


@app.route("/api/ai-call/auto-trigger", methods=["POST"])
def auto_trigger_call():
    data = request.json
    lead_id = data.get("leadId")
    lead_name = data.get("leadName", "Unknown")
    company_name = data.get("companyName", "Unknown Company")
    phone = data.get("phone", "")

    call_id = str(uuid.uuid4())
    opening_message = f"Hello! I'm an AI assistant calling from {COMPANY_PROFILE['name']}. May I speak with {lead_name} from {company_name}?"

    active_calls[call_id] = {
        "lead_id": lead_id,
        "lead_name": lead_name,
        "company_name": company_name,
        "phone": phone,
        "start_time": datetime.utcnow().isoformat(),
        "start_ts": time.time(),
        "system_prompt": build_system_prompt(lead_name, company_name),
        "conversation": [{"role": "assistant", "content": opening_message}],
        "status": "active",
        "question_index": 0,
    }

    def run_simulation():
        time.sleep(1)
        simulated_responses = [
            f"Yes, this is {lead_name}.",
            "We use basic CRM tools but they're not well integrated.",
            "About a 4 out of 10 — a lot of manual work.",
            "Around 150 leads per month.",
            "Yes, we'd be open to an AI solution.",
            "Budget around $300 to $800 per month.",
            "Please follow up via email.",
        ]
        for msg in simulated_responses:
            generate_ai_response(call_id, msg)
            if len(active_calls.get(call_id, {}).get("conversation", [])) >= 14:
                break
        if call_id in active_calls:
            active_calls[call_id]["status"] = "ended"
            generate_call_report(call_id)

    threading.Thread(target=run_simulation, daemon=True).start()

    return jsonify({
        "callId": call_id,
        "status": "auto-triggered",
        "message": opening_message,
        "leadId": lead_id,
    })


@app.route("/api/ai-call/all-reports", methods=["GET"])
def get_all_reports():
    return jsonify(list(call_reports.values()))


@app.route("/api/ai-call/active-calls", methods=["GET"])
def get_active_calls():
    return jsonify([
        {"callId": k, "leadName": v["lead_name"], "status": v["status"], "startTime": v["start_time"]}
        for k, v in active_calls.items()
    ])


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "groq": "connected" if groq_client else "no-key-set"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9080, debug=True)