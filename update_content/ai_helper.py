import os
import openai

# OpenAI API Configuration
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = "https://veeravn-ai.openai.azure.com"
DEPLOYMENT_NAME = "gpt-4o"

client = openai.AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-03-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

def generate_ai_job_description(title, company, team, technologies):
    """Generates an AI-powered job description using OpenAI"""
    prompt = f"""
    Generate a professional job description for the role of {title} at {company} in the {team} team.
    Highlight key responsibilities, technical expertise in {technologies}, and overall impact.
    """

    ai_response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    return ai_response.choices[0].message.content.strip()
