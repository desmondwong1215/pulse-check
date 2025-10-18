import os
import json
import random
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

def generate_technical_question(employee_path, employee, summary):
    """
    Use OpenAI to choose the next best technical question with few considerations:
    1) employee data
    2) employee historical answer summary
    """

    try:
        # read the general_question_prompt
        with open("prompts\\technical_question_prompt.txt", 'r') as file:
            template_string = file.read()

        # fit in employee_data and historical_summary, generate data
        prompt = template_string.format(employee=employee, summary=summary)
        data = {
            "model": MODEL,
            "messages": [
                {"role": "user", "content": prompt},
            ],
        }

        # get AI-generated general question
        # Use json.dumps() to convert the Python dictionary to a JSON string for the body
        response = requests.post(AZURE_ENDPOINT_URL, headers=HEADERS, data=json.dumps(data))
        response.raise_for_status() 
        response_json = response.json()
        new_question = response_json['choices'][0]['message']['content']

        # internal usage (for debugging)
        print("\n--- Model Response ---")
        print(new_question)
        print("\n--- Usage Info ---")
        print(f"Total tokens used: {response_json.get('usage', {}).get('total_tokens', 'N/A')}")

        # store the general question into the file
        write_data(employee_path + "\\question.json", json.loads(new_question))

    except FileNotFoundError:
        print("Error: 'prompts\\technical_question_prompt.txt' not found.")

    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        if response.status_code == 401:
            print("ACTION REQUIRED: Check your Ocp-Apim-Subscription-Key for the Azure API Gateway.")
        else:
            print(f"Server response:\n{response.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ An error occurred during the network request: {e}")

    except Exception as e:
        print(e, "hello world")


def generate_general_question(employee_path, employee, summary):
    """
    Use OpenAI to choose the next best general question with few considerations:
    1) employee data
    2) employee historical answer summary
    """

    try:
        # read the general_question_prompt
        with open("prompts\\general_question_prompt.txt", 'r') as file:
            template_string = file.read()

        # fit in employee_data and historical_summary, generate data
        prompt = template_string.format(employee=employee, summary=summary)
        data = {
            "model": MODEL,
            "messages": [
                {"role": "user", "content": prompt},
            ],
        }

        # get AI-generated general question
        # Use json.dumps() to convert the Python dictionary to a JSON string for the body
        response = requests.post(AZURE_ENDPOINT_URL, headers=HEADERS, data=json.dumps(data))
        response.raise_for_status() 
        response_json = response.json()
        new_question = response_json['choices'][0]['message']['content']

        # internal usage (for debugging)
        print("\n--- Model Response ---")
        print(new_question)
        print("\n--- Usage Info ---")
        print(f"Total tokens used: {response_json.get('usage', {}).get('total_tokens', 'N/A')}")

        write_data(employee_path + "\\question.json", json.loads(new_question))

    except FileNotFoundError:
        print("Error: 'prompts\\general_question_prompt.txt' not found.")

    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        if response.status_code == 401:
            print("ACTION REQUIRED: Check your Ocp-Apim-Subscription-Key for the Azure API Gateway.")
        else:
            print(f"Server response:\n{response.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ An error occurred during the network request: {e}")

    except Exception as e:
        print(e, "hello world")

@app.route("/get-employees", methods=["GET"])
def get_employees():
    employees = read_data("data\\employees.json")
    return jsonify(employees)


@app.route("/get-question", methods=["POST"])
def get_question():
    body = request.get_json(silent=True) or {}
    employee_id = body.get("employee_id")
    if not employee_id:
        return jsonify({"error": "employee_id is required"}), 400
    
    path = "data\\employees\\" + employee_id
    question = read_data(path + "\\question.json")

    if not question:
        print("No questions available to select.")
        return jsonify({"error": "No questions available"}), 404

    return jsonify(question)


@app.route("/submit-answer", methods=["POST"])
def submit_answer():
    body = request.get_json(silent=True) or {}
    employee_id = body.get("employee_id")
    result = body.get("result")

    if not employee_id or result is None:
        print("error: employee_id and result are required")
        return jsonify({"error": "employee_id and result are required"}), 400

    path = "data\\employees\\" + employee_id

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    new_answer = {
        "employee_id": employee_id,
        "result": result,
        "answered_at": timestamp,
    }

    write_data(path + "\\answers.json", new_answer)

    is_technical_question = random.random()
    employee = json.dumps(read_data(path + "\\profile.json"), indent=4)
    summary = str(new_answer)
    if is_technical_question >= 0.5:
        print("generate technical question")
        generate_technical_question(path, employee, summary)
    else:
        print("generate general question")
        generate_general_question(path, employee, summary)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
