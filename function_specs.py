# File: function_specs.py

FUNCTION_SPECS = [
    {
        "name": "add_project",
        "description": "Add a new project entry to the portfolio's Projects section.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The identifier of the user (defaults to the portfolio user).",
                    "default": "portfolio_user"
                },
                "project": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the project."
                        },
                        "description": {
                            "type": "string",
                            "description": "A brief summary of what the project does."
                        },
                        "link": {
                            "type": "string",
                            "description": "URL where the project is hosted or its repo."
                        },
                        "technologies": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of technologies used in this project."
                        }
                    },
                    "required": ["title", "description", "technologies"]
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
                "user_id": {
                    "type": "string",
                    "description": "The identifier of the user (defaults to the default user).",
                    "default": "default_user"
                },
                "experience": {
                    "type": "object",
                    "properties": {
                        "role": {
                            "type": "string",
                            "description": "Job title or role held."
                        },
                        "company": {
                            "type": "string",
                            "description": "Name of the company."
                        },
                        "start_date": {
                            "type": "string",
                            "description": "When the role started (e.g. '2022')."
                        },
                        "end_date": {
                            "type": "string",
                            "description": "When the role ended or 'Present'."
                        },
                        "description": {
                            "type": "string",
                            "description": "Brief summary of responsibilities and achievements."
                        },
                        "environment": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of technologies and tools used in this role."
                        }
                    },
                    "required": ["role", "company", "start_date", "description", "environment"]
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