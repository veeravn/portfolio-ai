import os
import openai
import azure.functions as func
import json

# Load API Key from Environment Variable
api_key = os.getenv("AZURE_OPENAI_KEY")
openai_endpoint = "https://veeravn-ai.openai.azure.com"
deployment_name = "gpt-4o"

if not api_key:
    raise ValueError("ERROR: AZURE_OPENAI_KEY is missing in environment variables!")

client = openai.AzureOpenAI(
    api_key=api_key,
    api_version="2024-03-01-preview",
    azure_endpoint=openai_endpoint,
)

def main(req: func.HttpRequest, res: func.Out[str]) -> None:
    """Azure Function to process user input for Copilot chatbot"""
    
    try:
        req_body = req.get_json()
    except ValueError:
        res.set(json.dumps({"error": "Invalid JSON request"}))
        return

    user_message = req_body.get("message", "").strip()
    if not user_message:
        res.set(json.dumps({"error": "No message provided"}))
        return

    # Generate AI response
    ai_response = client.chat.completions.create(
        model=deployment_name,
        messages=[{"role": "user", "content": user_message}]
    )
    reply = ai_response.choices[0].message.content.strip()

    # Set the response parameter
    res.set(json.dumps({"response": reply}))