import json
import logging
import azure.functions as func
from openai import OpenAI
from tools import TOOLS, FUNCTION_SPECS

# Initialize OpenAI client once
client = OpenAI()

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
            model="gpt-4o-mini",
            messages=messages,
            functions=FUNCTION_SPECS,
            function_call="auto"
        )
        msg = chat_resp.choices[0].message

        if msg.get("function_call"):
            name = msg.function_call.name
            args = json.loads(msg.function_call.arguments)
            result = TOOLS[name](**args)

            # Add function output and get the final reply
            messages.append({
                "role": "function",
                "name": name,
                "content": json.dumps(result)
            })
            followup = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            agent_reply = followup.choices[0].message.content
        else:
            agent_reply = msg.content

        # Persist updated session
        TOOLS["save_user_session"](user_id=user_id, session_data={"history": messages})

        return func.HttpResponse(
            json.dumps({"reply": agent_reply}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("Agent error")
        return func.HttpResponse(str(e), status_code=500)
