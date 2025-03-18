import os
import openai
import azure.functions as func
import json
from github import Github
from bs4 import BeautifulSoup

# Load API Keys from Azure Environment
api_key = os.getenv("AZURE_OPENAI_KEY")
github_token = os.getenv("GITHUB_TOKEN")

if not api_key:
    raise ValueError("ERROR: AZURE_OPENAI_KEY is missing in environment variables!")


# Azure OpenAI configuration
openai_endpoint = "https://veeravn-ai.openai.azure.com"
deployment_name = "gpt-4o"

client = openai.AzureOpenAI(
    api_key=api_key,
    api_version="2024-03-01-preview",
    azure_endpoint=openai_endpoint,
)

openai.api_type = "azure"
openai.api_version = "2024-03-01" # or other versions
openai.api_key = api_key

# GitHub Repository
GITHUB_REPO = "veeravn/veeravn.github.io"
INDEX_FILE_PATH = "index.html"

def get_company_url(company_name):
    """Use OpenAI to find the company's official website"""
    ai_prompt = f"""
    Find the official website URL for the company named '{company_name}'.
    If the company has multiple websites, return the one that is most commonly used as the official corporate website.
    Only provide the URL without any extra text.
    """

    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[{"role": "user", "content": ai_prompt}]
        )
        company_url = response.choices[0].message.content.strip()
        
        # Validate the response (must be a proper URL)
        if company_url.startswith("http"):
            return company_url
    except Exception as e:
        print(f"Error finding company URL with OpenAI: {e}")

    # Fallback if OpenAI fails
    return f"https://www.google.com/search?q={company_name.replace(' ', '+')}"

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function to update index.html with AI-generated content"""

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(json.dumps({"error": "Invalid JSON request body"}), 
                                 status_code=400, mimetype="application/json")

    # Extract user-provided experience details
    title = req_body.get("title", "Software Engineer")
    company = req_body.get("company", "Company Name")
    company_url = req_body.get("company_url")  # Use OpenAI if missing
    team_name = req_body.get("team_name", "Engineering Team")
    year_range = req_body.get("year_range", "(2020 - 2024)")
    environment = req_body.get("environment", "Python, Azure, Cloud")

    # Auto-fetch company URL if missing
    if not company_url:
        company_url = get_company_url(company)


    # Construct AI prompt for job description
    ai_prompt = f"""
    Generate a compelling job description for a {title} at {company}, within the {team_name}.
    The key technologies used in this role are: {environment}.
    Provide a short, engaging paragraph for a resume that highlights contributions to the team.  
    Return only the resume contribution paragraph
    Make it concise and to the point.  Return as html p tag instead of markdown
    """

    # Call OpenAI to generate job description
    ai_response = client.chat.completions.create(
        model=deployment_name,
        messages=[{"role": "user", "content": ai_prompt}]
    )
    description = ai_response.choices[0].message.content
    

    # Construct a new experience entry
    new_experience_html = f"""
    <div class="item">
        <h3 class="title">{title} - <span class="place"><a href="{company_url}">{company}</a></span> <span class="year">{year_range}</span></h3>
        {description}
    </div>
    """
    
    # Update index.html in GitHub
    res = update_index_html(new_experience_html)

    if "Error: " in res:
        print(res)

    # return func.HttpResponse(json.dumps({"status": "index.html updated"}), 
    #                          status_code=200, mimetype="application/json")
    return None

def update_index_html(new_experience_html):
    """Updates index.html in the GitHub repository using BeautifulSoup"""
    g = Github(github_token)
    repo = g.get_repo(GITHUB_REPO)

    try:
        file = repo.get_contents(INDEX_FILE_PATH)
        old_content = file.decoded_content.decode("utf-8")
    except:
        return "Error: index.html not found."

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(old_content, "html.parser")

    # Find the experience section
    experience_section = soup.find("section", class_="experience section")
    if not experience_section:
        return "Error: Experience section not found."

    # Find the section-inner div
    section_inner = experience_section.find("div", class_="section-inner")
    if not section_inner:
        return "Error: section-inner div not found."

    # Find the content div
    content_div = section_inner.find("div", class_="content")
    if not content_div:
        return "Error: content div not found."

    # Add new experience entry inside the content div
    content_div.append(BeautifulSoup(new_experience_html, "html.parser"))
    
    # Convert updated HTML back to string
    updated_content = str(soup)

    # Commit updated index.html to GitHub
    commit = repo.update_file(INDEX_FILE_PATH, "AI-updated experience section", updated_content, file.sha)
    print({commit["commit"]})
    return "Updated index.html successfully"
