"""Defines available tools and their JSON schemas for OpenAI function calling."""
import json
from copilot.session_manager import get_user_session, save_user_session, delete_user_session
from copilot.ai_helper import generate_ai_response


TOOLS = {
    "get_user_session":    get_user_session,
    "save_user_session":   save_user_session,
    "generate_ai_response": generate_ai_response,
    "delete_user_session": delete_user_session
}

