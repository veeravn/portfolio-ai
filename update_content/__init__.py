import json
import azure.functions as func
from .github_helper import update_index_html
from .ai_helper import generate_ai_job_description
from .html_parser import generate_project_html, generate_work_experience_html

def main(req: func.HttpRequest, res: func.Out[func.HttpResponse]) -> None:
    """Azure Function to update the 'Other Projects' or 'Work Experience' section in index.html"""

    try:
        req_body = req.get_json()
    except ValueError:
        res.set(func.HttpResponse(json.dumps({"error": "Invalid JSON request"}), status_code=400, mimetype="application/json"))
        return

    content_type = req_body.get("type", "").strip().lower()

    if content_type == "project":
        project_data = {
            "title": req_body.get("title", "").strip(),
            "description": req_body.get("description", "").strip(),
            "technologies": req_body.get("technologies", "").strip(),
            "link": req_body.get("link", "#").strip()
        }

        if not all(project_data.values()):
            res.set(func.HttpResponse(json.dumps({"error": "Missing required fields for project"}), status_code=400, mimetype="application/json"))
            return

        new_content_html = generate_project_html(**project_data)
        update_result = update_index_html(new_content_html, "projects section")

    elif content_type == "work":
        work_data = {
            "title": req_body.get("title", "").strip(),
            "company": req_body.get("company", "").strip(),
            "team_name": req_body.get("team_name", "").strip(),
            "company_url": req_body.get("company_url", "#").strip(),
            "year_range": req_body.get("year_range", "").strip(),
            "technologies": req_body.get("technologies", "").strip()
        }

        if not all(work_data.values()):
            res.set(func.HttpResponse(json.dumps({"error": "Missing required fields for work experience"}), status_code=400, mimetype="application/json"))
            return

        # AI-generated description if missing
        if not req_body.get("description"):
            work_data["description"] = generate_ai_job_description(work_data["title"], work_data["company"], work_data["team_name"], work_data["technologies"])
        else:
            work_data["description"] = req_body.get("description", "").strip()

        new_content_html = generate_work_experience_html(**work_data)
        update_result = update_index_html(new_content_html, "work experience")

    else:
        res.set(func.HttpResponse(json.dumps({"error": "Invalid type. Must be 'project' or 'work'."}), status_code=400, mimetype="application/json"))
        return

    res.set(func.HttpResponse(json.dumps(update_result), mimetype="application/json", status_code=200))
