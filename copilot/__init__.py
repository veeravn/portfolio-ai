import json
import logging
import azure.functions as func
from openai import AzureOpenAI
import os
from .tools import TOOLS
from .logging_helper import log_info
from function_specs import FUNCTION_SPECS
from update_content.ai_helper import add_project, add_experience

# Extend the tool registry at runtime
TOOLS.update({
    "add_project":    add_project,
    "add_experience": add_experience,
})

# Initialize OpenAI client once
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = "https://veeravn-ai.openai.azure.com/"
DEPLOYMENT_NAME = "gpt-4o"
client = AzureOpenAI(
    api_key    = AZURE_OPENAI_KEY,        # or OPENAI_API_KEY
    azure_endpoint   = AZURE_OPENAI_ENDPOINT,   # must end in a slash
    api_version= "2023-06-01-preview"
)

async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        user_id = body.get("user_id")
        user_message = body.get("message")

        # Build conversation history
        messages = [{"role": "system", "content": "You are an AI agent for managing a portfolio website."}]
        session = TOOLS["get_user_session"](user_id=user_id)
        for msg in session.get("history", []):
            messages.append(msg)
        messages.append({"role": "user", "content": user_message})

        # Ask model to choose a tool or reply directly
        chat_resp = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            functions=FUNCTION_SPECS,
            function_call="auto"
        )
        msg = chat_resp.choices[0].message

        if msg.function_call:
            # a function call was returned
            name = msg.function_call.name
            args = json.loads(msg.function_call.arguments)
            args.setdefault("user_id", user_id)  # Ensure user_id is passed to the function
            result = await TOOLS[name](**args)

            messages.append({
                "role": "function",
                "name": name,
                "content": json.dumps(result)
            })
            followup = client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=messages
            )
            agent_reply = followup.choices[0].message.content

            # Only _after_ a successful commit, clear the session
            if result.get("status") == "success":
                user_id = args.get("user_id", "portfolio_user")
                TOOLS["delete_user_session"](user_id=user_id)
        else:
            agent_reply = msg.content

        log_info(f"[agent] user_id={user_id} message={user_message} agent_reply={agent_reply}")
        # Persist updated session
        TOOLS["save_user_session"](user_id=user_id, session_data={"history": messages})

        return func.HttpResponse(
            json.dumps({"response": agent_reply}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("Agent error")
        return func.HttpResponse(str(e), status_code=500)
