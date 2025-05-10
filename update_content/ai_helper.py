# File: update_content/ai_helper.py

import json

import logging as log
from .html_parser import read_portfolio_html, insert_project, insert_experience
from .github_helper import commit_html
from copilot.session_manager import delete_user_session

async def add_project(project: dict, user_id: str = "portfolio_user") -> dict:
    html    = read_portfolio_html(user_id)
    updated = insert_project(html, project)

    try:
        commit_result = commit_html(updated, "projects")
    except Exception as e:
        # If it’s an HTTPError from requests, grab the JSON body if possible
        body = getattr(e, "response", None)
        detail = body.text if body is not None else str(e)
        log.error(f"[add_project] GitHub commit failed: {detail}")
        return {
            "status": "error",
            "error": detail
        }
    log.info(f"[add_project] commit_html result: {commit_result}")

    # Clear out the in-flight session now that the work is done
    try:
        delete_user_session(user_id)
    except Exception as e:
        # Log or ignore—failure to delete is non-fatal
        print(f"[add_project] failed to delete session: {e}")

    return {
        "status":     "success",
        "section":    "projects",
        "project":    project,
        "commit_url": commit_result.get("content", {}).get("html_url")
    }

async def add_experience(experience: dict, user_id: str = "portfolio_user") -> dict:
    """
    Reads the user's portfolio HTML, inserts a new experience entry,
    and commits the updated HTML back to GitHub.
    """
    html = read_portfolio_html(user_id)
    updated = insert_experience(html, experience)
    try:
        commit_result = commit_html(updated, "experience")
    except Exception as e:
        log.error(f"[add_experience] commit_html threw: {e}")
        return {
            "status": "error",
            "error": f"GitHub commit exception: {e}"
        }
    if not commit_result.get("commit_url") and not commit_result.get("sha"):
        log.error(f"[add_experience] commit_html returned failure: {commit_result}")
        return {
            "status": "error",
            "error": f"GitHub commit failed: {commit_result}"
        }
    log.info(f"[add_experience] commit_html result: {commit_result}")

    try:
        delete_user_session(user_id)
    except Exception as e:
        print(f"[add_experience] failed to delete session: {e}")
    
    return {
        "status": "success",
        "section": "experience",
        "experience": experience,
        "commit": commit_result
    }
