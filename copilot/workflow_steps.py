workflow_steps = {
    "project": [
        ("ask_name", "What is your name?"),
        ("ask_project_name", "Nice to meet you, {name}! What is the name of your project?"),
        ("ask_project_description", "Great! Can you give me a short description of your project?"),
        ("ask_technologies", "What technologies does this project use?"),
        ("generate_content", None),
    ],
    "work": [
        ("ask_name", "What is your name?"),
        ("ask_company_name", "Nice to meet you, {name}! What company do you work at?"),
        ("ask_title_name", "What is your role at {company_name}?"),
        ("ask_team_name", "Which team did you work with at {company_name}?"),
        ("ask_years", "How long did you work there? (Format: YYYY - YYYY)"),
        ("ask_technologies", "What technologies did you use in this role?"),
        ("generate_content", None),
    ],
}

def get_next_question(user_session, workflow):
    """Get the next question based on the workflow step."""
    current_step = user_session["step"]
    steps = workflow_steps[workflow]

    for i, (step, question) in enumerate(steps):
        if step == current_step and i + 1 < len(steps):
            next_step, next_question = steps[i + 1]
            user_session["step"] = next_step

            user_session.setdefault("name", "User")
            user_session.setdefault("company_name", "Company")
            user_session.setdefault("team_name", "Team")

            if next_question:
                return next_question.format(**user_session)

    return None  # No more questions, ready to generate content
