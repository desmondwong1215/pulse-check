import os
import json
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv()

AZURE_ENDPOINT_URL = os.getenv("AZURE_ENDPOINT_URL")
AZURE_SUBSCRIPTION_KEY = os.getenv("AZURE_SUBSCRIPTION_KEY")
MODEL = os.getenv("MODEL")

if not (AZURE_SUBSCRIPTION_KEY and AZURE_ENDPOINT_URL and MODEL):
    print("Error: AZURE_API_KEY not found in environment variables.")

HEADERS = {
    "Content-Type": "application/json",
    "api-key": AZURE_SUBSCRIPTION_KEY 
}

def _path(filename: str) -> str:
    return os.path.join(BASE_DIR, filename)


def read_data(filename: str):
    with open(_path(filename), "r", encoding="utf-8") as f:
        return json.load(f)


def write_data(filename: str, data):
    with open(_path(filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _deterministic_next_question(employee, all_questions, answer_history):
    if not all_questions:
        return None

    # Build a map of last result per question id for this employee
    answers_by_qid = {}
    for ans in sorted(answer_history, key=lambda a: a.get("answered_at", "")):
        qid = ans.get("question_id")
        if qid is None:
            continue
        answers_by_qid[qid] = ans.get("result")

    answered_ids = set(answers_by_qid.keys())

    # 1) Prioritize incorrectly answered Technical questions (by lowest id)
    incorrect_technical = [
        q for q in all_questions
        if q.get("type") == "Technical" and answers_by_qid.get(q.get("id")) == "Incorrect"
    ]
    incorrect_technical.sort(key=lambda q: q.get("id", 0))
    if incorrect_technical:
        return incorrect_technical[0]

    # 2) New General questions (not yet answered)
    new_general = [
        q for q in all_questions
        if q.get("type") == "General" and q.get("id") not in answered_ids
    ]
    new_general.sort(key=lambda q: q.get("id", 0))
    if new_general:
        return new_general[0]

    # 3) New Technical questions (not yet answered)
    new_technical = [
        q for q in all_questions
        if q.get("type") == "Technical" and q.get("id") not in answered_ids
    ]
    new_technical.sort(key=lambda q: q.get("id", 0))
    if new_technical:
        return new_technical[0]

    # 4) Otherwise, just return the first question as a fallback
    return all_questions[0]


def get_ai_question(employee, all_questions, answer_history):
    """
    Use OpenAI to choose the next best question by ID following the priority:
    1) Incorrect Technical answers
    2) New General questions
    3) New Technical questions
    If AI is unavailable or fails, fall back to a deterministic selection.
    """

    try:

        # Prepare concise context for the model
        question_summaries = [
            {
                "id": q.get("id"),
                "type": q.get("type"),
                "skill_tag": q.get("skill_tag"),
                "text": q.get("text"),
            }
            for q in all_questions
        ]

        # Build a compact answer history
        history = [
            {
                "question_id": a.get("question_id"),
                "result": a.get("result"),
                "answered_at": a.get("answered_at"),
            }
            for a in answer_history
        ]

        system_message = (
            "You are an assistant that selects the next best question ID for an adaptive employee quiz. "
            "Strictly output only the numeric question ID with no extra text. "
            "Priorities: 1) Re-ask incorrectly answered Technical questions; 2) Ask unseen General questions; 3) Ask unseen Technical questions. "
            "If multiple candidates qualify, pick the lowest numeric ID."
        )

        user_message = {
            "employee": employee,
            "all_questions": question_summaries,
            "answer_history": history,
        }

        data = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": json.dumps(user_message)},
            ],
        }

        chosen_id = None
        try:
            # Use json.dumps() to convert the Python dictionary to a JSON string for the body
            response = requests.post(AZURE_ENDPOINT_URL, headers=HEADERS, data=json.dumps(data))
            
            # Check for HTTP errors (like 401 Unauthorized or 404 Not Found)
            response.raise_for_status() 

            # --- 5. PROCESS RESPONSE ---
            response_json = response.json()
            
            # The actual completion message is located in the 'choices' array
            assistant_reply = response_json['choices'][0]['message']['content']
            
            print("\n--- Model Response ---")
            print(assistant_reply)
            print("\n--- Usage Info ---")
            print(f"Total tokens used: {response_json.get('usage', {}).get('total_tokens', 'N/A')}")

            # Parse an integer ID from the response
            # Prefer exact integer; fall back to extracting first integer-like token
            chosen_id = int(assistant_reply)

        except requests.exceptions.HTTPError as e:
            print(f"\n❌ HTTP Error: {e}")
            if response.status_code == 401:
                print("ACTION REQUIRED: Check your Ocp-Apim-Subscription-Key for the Azure API Gateway.")
            else:
                print(f"Server response:\n{response.text}")
        except requests.exceptions.RequestException as e:
            print(f"\n❌ An error occurred during the network request: {e}")

        except Exception:
            import re
            m = re.search(r"\b(\d+)\b", assistant_reply)
            if m:
                chosen_id = int(m.group(1))

        if chosen_id is not None:
            q_by_id = {q.get("id"): q for q in all_questions}
            if chosen_id in q_by_id:
                return q_by_id[chosen_id]

        # If parsing failed or ID not found, fall back
        return _deterministic_next_question(employee, all_questions, answer_history)

    except Exception:
        # Any AI error -> deterministic fallback
        return _deterministic_next_question(employee, all_questions, answer_history)


@app.route("/get-employees", methods=["GET"])
def get_employees():
    employees = read_data("employees.json")
    return jsonify(employees)


@app.route("/get-question", methods=["POST"])
def get_question():
    body = request.get_json(silent=True) or {}
    employee_id = body.get("employee_id")
    if not employee_id:
        return jsonify({"error": "employee_id is required"}), 400

    employees = read_data("employees.json")
    questions = read_data("questions.json")
    answers = read_data("answers.json")

    employee = next((e for e in employees if e.get("id") == employee_id), None)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    employee_history = [a for a in answers if a.get("employee_id") == employee_id]

    next_question = get_ai_question(employee, questions, employee_history)
    if not next_question:
        return jsonify({"error": "No questions available"}), 404

    return jsonify(next_question)


@app.route("/submit-answer", methods=["POST"])
def submit_answer():
    body = request.get_json(silent=True) or {}
    employee_id = body.get("employee_id")
    question_id = body.get("question_id")
    result = body.get("result")

    if not employee_id or question_id is None or result is None:
        return jsonify({"error": "employee_id, question_id, and result are required"}), 400

    answers = read_data("answers.json")

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    new_answer = {
        "employee_id": employee_id,
        "question_id": question_id,
        "result": result,
        "answered_at": timestamp,
    }

    answers.append(new_answer)
    write_data("answers.json", answers)

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
