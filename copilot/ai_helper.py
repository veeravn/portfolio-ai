import os
import json
import requests
from openai import AzureOpenAI
from config.env import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, DEPLOYMENT_NAME, AZURE_OPENAI_API_VERSION

    
client = AzureOpenAI(
    api_key             = AZURE_OPENAI_KEY,        # or OPENAI_API_KEY
    azure_endpoint      = AZURE_OPENAI_ENDPOINT,   # must end in a slash
    api_version         = AZURE_OPENAI_API_VERSION
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
