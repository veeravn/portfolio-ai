import os
import json
import requests
from openai import AzureOpenAI


AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = "https://veeravn-ai.openai.azure.com/"
DEPLOYMENT_NAME = "gpt-4o"

client = AzureOpenAI(
    api_key    = AZURE_OPENAI_KEY,        # or OPENAI_API_KEY
    azure_endpoint   = AZURE_OPENAI_ENDPOINT,   # must end in a slash
    api_version= "2024-12-01"
)

update_content_url = "https://veeravnchatbotfunction.azurewebsites.net/api/update_content"

def generate_ai_response(messages: list, functions: list) -> dict:
    resp = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=messages,
        functions=functions,
        function_call="auto"
    )
    return resp.choices[0].message
