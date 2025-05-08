import os
import json
import requests
from openai import OpenAI


AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = "https://veeravn-ai.openai.azure.com"
DEPLOYMENT_NAME = "gpt-4o"

client = OpenAI(api_key=AZURE_OPENAI_KEY)

update_content_url = "https://veeravnchatbotfunction.azurewebsites.net/api/update_content"

def generate_ai_response(messages: list, functions: list) -> dict:
    resp = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=messages,
        functions=functions,
        function_call="auto"
    )
    return resp.choices[0].message
