import json, os
import azure.functions as func
from openai import OpenAI
from copilot.tools import FUNCTION_SPECS
from update_content.ai_helper import add_project, add_experience

# map function-call names to actual implementations
TOOLS = {
    "add_project": add_project,
    "add_experience": add_experience,
    # … other tools …
}

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def main(req: func.HttpRequest) -> func.HttpResponse:
    user_msg = await req.get_json()
    messages = user_msg["messages"]

    # ask the LLM which tool to call
    chat_resp = client.chat.completions.create(
        model=os.getenv("DEPLOYMENT_NAME"),
        messages=messages,
        functions=FUNCTION_SPECS,
        function_call="auto"
    )

    msg = chat_resp.choices[0].message
    if msg.finish_reason == "function_call":
        fn_name = msg.function_call.name
        args    = json.loads(msg.function_call.arguments)
        # dispatch to our helper
        result = await TOOLS[fn_name](**args)

        # feed the result back for a natural-language wrap-up
        followup = client.chat.completions.create(
            model=os.getenv("DEPLOYMENT_NAME"),
            messages=[
                *messages,
                {"role":"function", "name":fn_name, "content": json.dumps(result)}
            ]
        )
        reply = followup.choices[0].message.content
    else:
        reply = msg.content

    return func.HttpResponse(
        json.dumps({"reply": reply}),
        status_code=200,
        mimetype="application/json"
    )
