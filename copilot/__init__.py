import os
import openai
import azure.functions as func
import json
import requests

# Load API Keys
api_key = os.getenv("AZURE_OPENAI_KEY")
update_content_url = "https://veeravnchatbotfunction.azurewebsites.net/api/update_content"

if not api_key:
    raise ValueError("ERROR: AZURE_OPENAI_KEY is missing!")

client = openai.AzureOpenAI(
    api_key=api_key,
    api_version="2024-03-01-preview",
    azure_endpoint="https://veeravn-ai.openai.azure.com"
)

def send_update_request(update_text):
    """Send AI-generated content to update_content API"""
    payload = {"prompt": update_text}
    response = requests.post(update_content_url, json=payload, headers={"Content-Type": "application/json"})
    return response.json()

user_sessions = {} 

# Define the questions for both workflows (Project & Work Experience)
workflow_steps = {
    "project": [
        ("ask_name", "What is your name?"),
        ("ask_project_name", "Nice to meet you, {name}! What is the name of your project?"),
        ("ask_project_description", "Great! Can you give me a short description of your project?"),
        ("ask_technologies", "What technologies does this project use?"),
        ("generate_content", None),
    ],
    "work": [
        ("ask_name", "What is your name?"),
        ("ask_company_name", "Nice to meet you, {name}! What company do you work at?"),
        ("ask_title_name", "What is your role at {company_name}?"),
        ("ask_team_name", "Which team did you work with at {company_name}?"),
        ("ask_years", "How long did you work there? (Format: YYYY - YYYY)"),
        ("ask_technologies", "What technologies did you use in this role?"),
        ("generate_content", None),
    ],
}

def get_next_question(user_session, workflow):
    """Get the next question based on the workflow step."""
    current_step = user_session["step"]
    steps = workflow_steps[workflow]

    for i, (step, question) in enumerate(steps):
        if step == current_step and i + 1 < len(steps):
            next_step, next_question = steps[i + 1]
            user_session["step"] = next_step
            if next_question:
                # Replace placeholders (e.g., {name}, {company_name}) with user data
                return next_question.format(**user_session)

    return None  # No more questions, ready to generate content


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function to handle Copilot requests"""

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(json.dumps({"error": "Invalid JSON request"}), 
                                 status_code=400, mimetype="application/json")

    user_message = req_body.get("message", "").strip()
    user_id = req_body.get("user_id", "default_user")  # Unique user identifier

    if not user_message:
        return func.HttpResponse(json.dumps({"error": "No message provided"}), 
                                 status_code=400, mimetype="application/json")

    # Identify workflow type (Project or Work Experience)
    workflow = None
    if "add work experience" in user_message:
        workflow = "work"
    elif "add project" in user_message:
        workflow = "project"

    if workflow is None:
        return func.HttpResponse(json.dumps({"response": "I can help add projects or work experience! Try asking me."}), 
                                 mimetype="application/json", status_code=200)

    # Initialize user session if not exists
    if user_id not in user_sessions:
        user_sessions[user_id] = {"step": "ask_name", "workflow": workflow}

    user_session = user_sessions[user_id]

    # Store user input for the current step
    if user_session["step"] != "ask_name":  # Don't overwrite name before asking
        step_name = user_session["step"]
        user_session[step_name] = user_message

    # Get the next question or generate content
    next_question = get_next_question(user_session, workflow)

    if next_question:
        return func.HttpResponse(json.dumps({"response": next_question}), mimetype="application/json", status_code=200)

    # Step: Generate AI Content Once All Details Are Gathered
    if user_session["step"] == "generate_content":
        if workflow == "project":
            user_name = user_session["name"]
            project_name = user_session["ask_project_name"]
            project_description = user_session["ask_project_description"]
            technologies = user_session["ask_technologies"]

            update_request = {
                "type": workflow,
                "title": project_name,
                "description": project_description,
                "technologies": technologies,
            }

        elif workflow == "work":
            title = user_session["ask_title_name"]
            company = user_session["ask_company_name"]
            team = user_session["ask_team_name"]
            years = user_session["ask_years"]
            technologies = user_session["ask_technologies"]

            update_request = {
                "type": workflow,
                "title": title,
                "company": company,
                "team_name": team,
                "year_range": years,
                "technologies": technologies,
            }

        # Send the AI-generated content to update_content API
        update_response = send_update_request(json.dumps(update_request))

        # Clear user session after completion
        del user_sessions[user_id]

        return func.HttpResponse(json.dumps({"response": update_response}), mimetype="application/json", status_code=200)

    return func.HttpResponse(json.dumps({"response": "Something went wrong, please try again."}), 
                             mimetype="application/json", status_code=500)