import os
import openai
import requests

AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = "https://veeravn-ai.openai.azure.com"
DEPLOYMENT_NAME = "gpt-4o"

update_content_url = "https://veeravnchatbotfunction.azurewebsites.net/api/update_content"

client = openai.AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-03-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

def send_update_request(update_text):
    """Send AI-generated content to update_content API"""
    response = requests.post(update_content_url, json=update_text, headers={"Content-Type": "application/json"})
    print(response)
    return response.json()

def generate_ai_response(user_session, workflow):
    """Generates an AI-powered response based on session data."""
    prompt = f"""
    Generate a structured summary for a {workflow}.
    Name: {user_session.get("name", "Unknown")}.
    Company: {user_session.get("company_name", "Unknown")}.
    Team: {user_session.get("team_name", "Unknown")}.
    Technologies: {user_session.get("technologies", "None")}.
    """

    ai_response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    return ai_response.choices[0].message.content.strip()
