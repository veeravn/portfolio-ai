# File: function_specs.py

FUNCTION_SPECS = [
    {
        "name": "add_project",
        "description": "Add a new project entry to the portfolio's Projects section.",
        "parameters": {
            "type": "object",
            "properties": {
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
            "required": ["project"]
        }
    },
    {
        "name": "add_experience",
        "description": "Add a new work-experience entry to the portfolio's Experience section.",
        "parameters": {
            "type": "object",
            "properties": {
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
            "required": ["experience"]
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