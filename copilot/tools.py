"""Defines available tools and their JSON schemas for OpenAI function calling."""
import json
from .session_manager import get_user_session, save_user_session
from .ai_helper import generate_ai_response
from update_content.ai_helper import send_update_request
from update_content.html_parser import parse_html
from update_content.github_helper import commit_html

TOOLS = {
    "get_user_session": get_user_session,
    "save_user_session": save_user_session,
    "generate_ai_response": generate_ai_response,
    "send_update_request": send_update_request,
    "parse_html": parse_html,
    "commit_html": commit_html,
}

FUNCTION_SPECS = [
    {
        "name": "add_project",
        "description": "Add a new project entry to the portfolio's Projects section.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "project": {
                    "type": "object",
                    "properties": {
                        "title":       {"type": "string"},
                        "description": {"type": "string"},
                        "link":        {"type": "string"}
                    },
                    "required": ["title", "description"]
                }
            },
            "required": ["user_id", "project"]
        }
    },
    {
        "name": "add_experience",
        "description": "Add a new work-experience entry to the portfolio's Experience section.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "experience": {
                    "type": "object",
                    "properties": {
                        "role":        {"type": "string"},
                        "company":     {"type": "string"},
                        "start_date":  {"type": "string"},
                        "end_date":    {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["role", "company", "start_date", "description"]
                }
            },
            "required": ["user_id", "experience"]
        }
    },
    {
        "name": "get_user_session",
        "description": "Retrieve conversation state for a user.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Unique user identifier"}
            },
            "required": ["user_id"],
        },
    },
    {
        "name": "save_user_session",
        "description": "Persist conversation state for a user.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "session_data": {"type": "object"}
            },
            "required": ["user_id", "session_data"],
        },
    },
    {
        "name": "generate_ai_response",
        "description": "Generate the next AI response given the conversation history.",
        "parameters": {
            "type": "object",
            "properties": {
                "messages": {"type": "array", "items": {"type": "object"}},
                "functions": {"type": "array", "items": {"type": "object"}}
            },
            "required": ["messages", "functions"],
        },
    },
    {
        "name": "send_update_request",
        "description": "Process and commit new HTML content to GitHub Pages.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "html_content": {"type": "string"}
            },
            "required": ["user_id", "html_content"],
        },
    },
    {
        "name": "parse_html",
        "description": "Parse raw HTML into deployable components (path, content).",
        "parameters": {
            "type": "object",
            "properties": {
                "html": {"type": "string"}
            },
            "required": ["html"],
        },
    },
    {
        "name": "commit_html",
        "description": "Commit HTML file to GitHub repository.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["path", "content"],
        },
    }
]