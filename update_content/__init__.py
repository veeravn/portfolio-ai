import json, os
import azure.functions as func
from function_specs import FUNCTION_SPECS
from openai import AzureOpenAI
from update_content.ai_helper import add_project, add_experience

# map function-call names to actual implementations
TOOLS = {
    "add_project": add_project,
    "add_experience": add_experience,
    # … other tools …
}

AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = "https://veeravn-ai.openai.azure.com/"
DEPLOYMENT_NAME = "gpt-4.1"
client = AzureOpenAI(
    api_key             = AZURE_OPENAI_KEY,        # or OPENAI_API_KEY
    azure_endpoint      = AZURE_OPENAI_ENDPOINT,   # must end in a slash
    api_version         = "2025-01-01-preview"
)


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
