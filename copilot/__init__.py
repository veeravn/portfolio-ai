import os
import openai
import azure.functions as func
import json
import requests
from azure.data.tables import TableServiceClient, TableClient

# Load API Keys
api_key = os.getenv("AZURE_OPENAI_KEY")
update_content_url = "http://localhost:7071/api/update_content"

# Azure Table Storage Configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

if not AZURE_STORAGE_CONNECTION_STRING:
    raise ValueError("ERROR: AZURE_STORAGE_CONNECTION_STRING is missing!")
TABLE_NAME = "CopilotSessions"

if not api_key:
    raise ValueError("ERROR: AZURE_OPENAI_KEY is missing!")

client = openai.AzureOpenAI(
    api_key=api_key,
    api_version="2024-03-01-preview",
    azure_endpoint="https://veeravn-ai.openai.azure.com"
)

def send_update_request(update_text):
    """Send AI-generated content to update_content API"""
    response = requests.post(update_content_url, json=update_text, headers={"Content-Type": "application/json"})
    print(response)
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

# Function to get Azure Table Storage client
def get_table_client():
    service_client = TableServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    return service_client.get_table_client(TABLE_NAME)

# Function to fetch user session from Azure Table Storage
def get_user_session(user_id):
    table_client = get_table_client()
    try:
        session = table_client.get_entity(partition_key="session", row_key=user_id)
        return json.loads(session["Data"])
    except:
        return None  # Return None if session does not exist

# Function to save user session to Azure Table Storage
def save_user_session(user_id, session_data):
    table_client = get_table_client()
    entity = {
        "PartitionKey": "session",
        "RowKey": user_id,
        "Data": json.dumps(session_data)
    }
    table_client.upsert_entity(entity)

def get_next_question(user_session, workflow):
    """Get the next question based on the workflow step."""
    current_step = user_session["step"]
    steps = workflow_steps[workflow]

    for i, (step, question) in enumerate(steps):
        if step == current_step and i + 1 < len(steps):
            next_step, next_question = steps[i + 1]
            user_session["step"] = next_step

            # Ensure placeholders are replaced correctly
            user_session.setdefault("name", "User")
            user_session.setdefault("company_name", "Company")
            user_session.setdefault("team_name", "Team")

            if next_question:
                return next_question.format(**user_session)

    return None  # No more questions, ready to generate content

def main(req: func.HttpRequest, res: func.Out[func.HttpResponse]) -> None:
    try:
        req_body = req.get_json()
    except ValueError:
        res.set(func.HttpResponse(json.dumps({"error": "Invalid JSON request"}), 
                                  status_code=400, mimetype="application/json"))
        return

    user_id = req_body.get("user_id", "default_user")
    user_message = req_body.get("message", "").strip().lower()

    if not user_message:
        res.set(func.HttpResponse(json.dumps({"error": "No message provided"}), 
                                  status_code=400, mimetype="application/json"))
        return

    # Fetch existing session or initialize new one
    user_session = get_user_session(user_id)

    # If no session exists, check for workflow type in the message
    if not user_session:
        workflow = None
        if "add work experience" in user_message:
            workflow = "work"
        elif "add project" in user_message:
            workflow = "project"

        if workflow is None:
            res.set(func.HttpResponse(json.dumps({"response": "I can help add projects or work experience! Try asking me."}), 
                                      mimetype="application/json", status_code=200))
            return

        # Initialize a new session
        first_step, first_question = workflow_steps[workflow][0]
        user_session = {"step": first_step, "workflow": workflow}

        # Save the session immediately
        save_user_session(user_id, user_session)

        res.set(func.HttpResponse(json.dumps({"response": first_question}), mimetype="application/json", status_code=200))
        return

    workflow = user_session["workflow"]  # Retrieve existing workflow

    # Store user input for the current step
    if user_session["step"] != "ask_name":
        step_name = user_session["step"]
        user_session[step_name] = user_message

    # Get the next question or generate content
    next_question = get_next_question(user_session, workflow)

    if next_question:
        save_user_session(user_id, user_session)  # Save session update
        res.set(func.HttpResponse(json.dumps({"response": next_question}), mimetype="application/json", status_code=200))
        return

    # Step: Generate AI Content Once All Details Are Gathered
    if user_session["step"] == "generate_content":
        # Clear session after completion
        save_user_session(user_id, {})  # Reset session
        if workflow == "project":
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
        update_response = send_update_request(update_request)
        print(update_response)

        # Clear user session after completion
        # del user_sessions[user_id]

        res.set(func.HttpResponse(json.dumps({"response": update_response}), mimetype="application/json", status_code=200))
        return

    res.set(func.HttpResponse(json.dumps({"response": "Something went wrong, please try again."}), 
                             mimetype="application/json", status_code=500))
    workflow = None
    return