# File: update_content/ai_helper.py

import json

import logging as log
from .html_parser import read_portfolio_html, insert_project, insert_experience
from .github_helper import commit_html

async def add_project(project: dict, user_id: str = "portfolio_user") -> dict:
    """
    Reads the user's portfolio HTML, inserts a new project card,
    and commits the updated HTML back to GitHub.
    """
    html = read_portfolio_html(user_id)
    updated = insert_project(html, project)
    try:
        commit_result = commit_html(updated, "projects")
    except Exception as e:
        log.error(f"[add_project] commit_html threw: {e}")
        return {
            "status": "error",
            "error": f"GitHub commit exception: {e}"
        }
    
    if not commit_result.get("commit_url") and not commit_result.get("sha"):
        log.error(f"[add_project] commit_html returned failure: {commit_result}")
        return {
            "status": "error",
            "error": f"GitHub commit failed: {commit_result}"
        }
    log.info(f"[add_project] commit_html result: {commit_result}")
    return {"status": "success", "section": "projects", "project": project, "commit": commit_result}

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
    return {
        "status": "success",
        "section": "experience",
        "experience": experience,
        "commit": commit_result
    }
