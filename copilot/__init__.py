import json
import azure.functions as func
from .session_manager import get_user_session, save_user_session
from .ai_helper import generate_ai_response, send_update_request
from .workflow_steps import get_next_question, workflow_steps
from .logging_helper import log_error

def main(req: func.HttpRequest, res: func.Out[func.HttpResponse]) -> None:
    """Azure Function to handle Copilot requests"""

    try:
        req_body = req.get_json()
    except ValueError:
        res.set(func.HttpResponse(json.dumps({"error": "Invalid JSON request"}), 
                                  status_code=400, mimetype="application/json"))
        return

    user_id = req_body.get("user_id", "default_user")
    user_message = req_body.get("message", "").strip()

    if not user_message:
        res.set(func.HttpResponse(json.dumps({"error": "No message provided"}), 
                                  status_code=400, mimetype="application/json"))
        return

    # Fetch existing session or initialize a new one
    user_session = get_user_session(user_id)

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

        first_step, first_question = workflow_steps[workflow][0]
        user_session = {"step": first_step, "workflow": workflow}

        save_user_session(user_id, user_session)

        res.set(func.HttpResponse(json.dumps({"response": first_question}), mimetype="application/json", status_code=200))
        return

    workflow = user_session["workflow"]

    # Store user input for the current step
    if user_session["step"] != "ask_name":
        step_name = user_session["step"]
        user_session[step_name] = user_message

    next_question = get_next_question(user_session, workflow)

    if next_question:
        save_user_session(user_id, user_session)
        res.set(func.HttpResponse(json.dumps({"response": next_question}), mimetype="application/json", status_code=200))
        return

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

        save_user_session(user_id, {})  # Clear session after completion

        res.set(func.HttpResponse(json.dumps({"response": update_response}), mimetype="application/json", status_code=200))
        return

    log_error("Unexpected error in Copilot function")
    res.set(func.HttpResponse(json.dumps({"response": "Something went wrong, please try again."}), 
                              mimetype="application/json", status_code=500))
