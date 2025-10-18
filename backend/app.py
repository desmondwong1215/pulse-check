import asyncio
import math
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
    
def read_txt(filename: str):
    with open(_path(filename), "r", encoding="utf-8") as f:
        return f.read()


def write_data(filename: str, data):
    with open(_path(filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


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
            ]
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
        print(e)

def generate_skill_question(employee_path, employee, summary):
    """
    Use OpenAI to choose the next best skill question with few considerations:
    1) employee data
    2) employee historical answer summary
    3) Skill sets required by PSA
    """

    try:
        # read the general_question_prompt
        with open("prompts\\skills_question_prompt.txt", 'r') as file:
            template_string = file.read()

        skills = read_data("data\\skills.json")

        # fit in employee_data and historical_summary, generate data
        prompt = template_string.format(employee=employee, summary=summary, skills=skills)
        data = {
            "model": MODEL,
            "messages": [
                {"role": "user", "content": prompt},
            ]
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
        print(e)

def generate_general_question(employee_path, employee, summary):
    """
    Use OpenAI to choose the next best general question with few considerations:
    1) employee data
    2) employee historical answer summary
    """

    try:
        # read the general_question_prompt
        template_string = read_txt("prompts\\general_question_prompt.txt")


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
        print(e)

def generate_performance_summary(employee, summary):

    try:
        # read the general_question_prompt
        template_string = read_txt("prompts\\performance_summary_prompt.txt")

        # fit in employee_data and historical_summary, generate data
        prompt = template_string.format(profile=employee, summary=summary)
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
        answer = response_json['choices'][0]['message']['content']

        # internal usage (for debugging)
        print("\n--- Model Response ---")
        print(answer)
        print("\n--- Usage Info ---")
        print(f"Total tokens used: {response_json.get('usage', {}).get('total_tokens', 'N/A')}")

    except FileNotFoundError:
        print("Error: 'prompts\\performance_summary_prompt.txt' not found.")

    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        if response.status_code == 401:
            print("ACTION REQUIRED: Check your Ocp-Apim-Subscription-Key for the Azure API Gateway.")
        else:
            print(f"Server response:\n{response.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ An error occurred during the network request: {e}")

    except Exception as e:
        print(e)
    
    return answer

def generate_feedback(employee, summary, question, answer, options):

    try:
        # read the general_question_prompt
        template_string = read_txt("prompts\\feedback_prompt.txt")

        # fit in employee_data and historical_summary, generate data
        prompt = template_string.format(employee=employee, summary=summary, question=question, answer=answer, options=options)
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
        feedback = response_json['choices'][0]['message']['content']

        # internal usage (for debugging)
        print("\n--- Model Response ---")
        print(feedback)
        print("\n--- Usage Info ---")
        print(f"Total tokens used: {response_json.get('usage', {}).get('total_tokens', 'N/A')}")

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
        print(e)
    return feedback

def get_answer_summary(employee, curr_question, answer, old_answer_summary):
    try:
        system_message = read_txt("prompts\\answer_summary_prompt.txt")

        user_message = {
            "employee": employee,
            "curr_question": curr_question,
            "answer": answer,
            "old_answer_summary": old_answer_summary,
        }

        data = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": json.dumps(user_message)},
            ],
        }

        res = None
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
            res = assistant_reply

        except requests.exceptions.HTTPError as e:
            print(f"\n❌ HTTP Error: {e}")
            if response.status_code == 401:
                print("ACTION REQUIRED: Check your Ocp-Apim-Subscription-Key for the Azure API Gateway.")
            else:
                print(f"Server response:\n{response.text}")
        except requests.exceptions.RequestException as e:
            print(f"\n❌ An error occurred during the network request: {e}")

        if res is not None:
            return res

        return old_answer_summary

    except Exception as e:
        print(f"Exception in get_answer_summary: {e}")
        return old_answer_summary

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

@app.route("/write-summary", methods=["POST"])
def write_summary():
    body = request.get_json(silent=True) or {}
    employee_id = body.get("employee_id")
    question = body.get("question")
    answer = body.get("answer")

    if not employee_id or question is None or answer is None:
        print("Missing required fields in the request body.")
        return jsonify({"error": "employee_id, question, and answer are required"}), 400
    
    path = "data\\employees\\" + employee_id
    employee = read_data(path + "\\profile.json")
    old_answer_summary = read_txt(path + "\\answer_summary.txt")
    answer_summary = get_answer_summary(employee, question, answer, old_answer_summary)

    write_data(path + "\\answer_summary.txt", answer_summary)
    generate_question(path, employee, answer_summary)
    return jsonify({"status": "ok"})

def generate_question(path, employee, summary):
    question_type = math.floor(random.random() * 3)
    print(question_type)
    if question_type == 0:
        print("generate technical question")
        generate_technical_question(path, employee, summary)
    elif question_type == 1:
        print("generate skill question")
        generate_skill_question(path, employee, summary)
    else:
        print("generate general question")
        generate_general_question(path, employee, summary)
    return jsonify({"status": "ok"})

@app.route("/get-feedback", methods=["POST"])
def get_feedback():
    body = request.get_json(silent=True) or {}
    employee_id = body.get("employee_id")
    question = body.get("question")
    answer = body.get("answer")
    options = body.get("options")
    path = "data\\employees\\" + employee_id
    employee = read_data(path + "\\profile.json")
    summary = read_txt(path + "\\answer_summary.txt")
    
    feeback = generate_feedback(employee, question, answer, summary, options)

    if not feeback:
        print("Feedback generation error.")
        return jsonify({"error": "No feedback generated"}), 404
    
    json_feedback = {
        "text" : feeback
    }

    return jsonify(json_feedback)

@app.route("/get-summary", methods=["POST"])
def get_answer():
    body = request.get_json(silent=True) or {}
    employee_id = body.get("employee_id")
    if not employee_id:
        return jsonify({"error": "employee_id is required"}), 400
    
    path = "data\\employees\\" + employee_id
    answersSummary = read_txt(path + "\\answer_summary.txt")
    profile = read_data(path + "\\profile.json")
    answersSummary = generate_performance_summary(profile, answersSummary)

    if not answersSummary:
        print("No answer summary to fetch.")
        return jsonify({"error": "No answer available"}), 404
    
    json_ans = {
        "text" : answersSummary
    }

    return jsonify(json_ans)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
