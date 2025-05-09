"""Defines available tools and their JSON schemas for OpenAI function calling."""
import json
from .session_manager import get_user_session, save_user_session
from .ai_helper import generate_ai_response


TOOLS = {
    "get_user_session":    get_user_session,
    "save_user_session":   save_user_session,
    "generate_ai_response": generate_ai_response,
}

