# File: update_content/ai_helper.py

import json
from .html_parser import read_portfolio_html, insert_project, insert_experience
from .github_helper import commit_html

async def add_project(project: dict, user_id: str = "portfolio_user") -> dict:
    """
    Reads the user's portfolio HTML, inserts a new project card,
    and commits the updated HTML back to GitHub.
    """
    html = read_portfolio_html(user_id)
    updated = insert_project(html, project)
    commit_result = commit_html(user_id, updated, section="projects")
    return {"status": "success", "section": "projects", "project": project, "commit": commit_result}

async def add_experience(experience: dict, user_id: str = "portfolio_user") -> dict:
    """
    Reads the user's portfolio HTML, inserts a new experience entry,
    and commits the updated HTML back to GitHub.
    """
    html = read_portfolio_html(user_id)
    updated = insert_experience(html, experience)
    commit_result = commit_html(user_id, updated, section="experience")
    return {
        "status": "success",
        "section": "experience",
        "experience": experience,
        "commit": commit_result
    }
