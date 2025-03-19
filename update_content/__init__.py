import os
import openai
import azure.functions as func
import json
from github import Github
from bs4 import BeautifulSoup

# GitHub API Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "veeravn/veeravn.github.io"
INDEX_FILE_PATH = "index.html"

# OpenAI API Configuration
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = "https://veeravn-ai.openai.azure.com"
DEPLOYMENT_NAME = "gpt-4o"

if not GITHUB_TOKEN or not AZURE_OPENAI_KEY:
    raise ValueError("ERROR: Missing required API keys!")

github_client = Github(GITHUB_TOKEN)

client = openai.AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-03-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

def fetch_index_html():
    """Fetch the latest version of index.html from GitHub"""
    repo = github_client.get_repo(GITHUB_REPO)
    file = repo.get_contents(INDEX_FILE_PATH)
    return file.decoded_content.decode("utf-8"), file.sha

def update_index_html(new_content_html, section_class):
    """Update index.html with new content in the specified section"""
    repo = github_client.get_repo(GITHUB_REPO)

    # Fetch latest version of index.html
    index_html, file_sha = fetch_index_html()

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(index_html, "html.parser")

    # Find the correct section by class name
    section = soup.find("section", class_=section_class)
    
    if not section:
        return {"error": f"Could not find the '{section_class}' section in index.html"}

    # Find the div with class="section-inner"
    section_inner_div = section.find("div", class_="section-inner")
    
    if not section_inner_div:
        return {"error": f"Could not find the 'section-inner' div in '{section_class}' section"}

    # Find the div with class="content"
    content_div = section_inner_div.find("div", class_="content")
    
    if not content_div:
        return {"error": f"Could not find the 'content' div inside the 'section-inner' div"}

    # Add new content at the end of the content div
    content_div.append(BeautifulSoup(new_content_html, "html.parser"))

    # Convert updated HTML back to string
    updated_html = str(soup)

    # Commit the updated index.html to GitHub
    response = repo.update_file(INDEX_FILE_PATH, f"Updated {section_class} section", updated_html, file_sha)
    commit = response['commit']
    print(commit.sha)
    return {"success": f"{section_class} updated successfully"}

def generate_ai_job_description(title, company, team_name, technologies):
    """Generates an AI-powered job description using OpenAI"""
    prompt = f"""
    Generate a compelling job description for a {title} at {company}, within the {team_name}.
    The key technologies used in this role are: {technologies}.
    Provide a short, engaging paragraph for a resume that highlights contributions to the team.  
    Return only the resume contribution paragraph
    Make it concise and to the point.  Return as html p tag instead of markdown
    """

    ai_response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    return ai_response.choices[0].message.content.strip()

def get_company_url(company_name):
    """Use OpenAI to find the company's official website"""
    ai_prompt = f"""
    Find the official website URL for the company named '{company_name}'.
    If the company has multiple websites, return the one that is most commonly used as the official corporate website.
    Only provide the URL without any extra text.
    """

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
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

def main(req: func.HttpRequest, res: func.Out[func.HttpResponse]) -> None:
    """Azure Function to update the 'Other Projects' or 'Work Experience' section in index.html"""
    
    try:
        req_body = req.get_json()
        print(req_body)
    except ValueError:
        res.set(func.HttpResponse(json.dumps({"error": "Invalid JSON request"}), status_code=400, mimetype="application/json"))
        return

    content_type = req_body.get("type", "").strip().lower()
    print(content_type)
    if content_type == "project":
        project_title = req_body.get("title", "").strip()
        project_description = req_body.get("description", "").strip()
        technologies = req_body.get("technologies", "").strip()
        project_link = req_body.get("link", "").strip()

        if not all([project_title, project_description, technologies]):
            res.set(func.HttpResponse(json.dumps({"error": "Missing required fields for project (title, description, technologies, link)"}), status_code=400, mimetype="application/json"))
            return

        # Generate new project HTML snippet matching the requested format
        new_content_html = f"""
        <div class="item">
            <h3 class="title"><a href="{project_link}" target="_blank">{project_title}</a><!--<span class="label label-theme">Open Source</span>--></h3>
            <p class="summary">{project_description}<br/><b>Technology Stack - </b> {technologies}</p>
        </div>
        """

        # Update "Other Projects" section
        update_result = update_index_html(new_content_html, "projects section")

    elif content_type == "work":
        job_title = req_body.get("title", "").strip()
        company = req_body.get("company", "").strip()
        team_name = req_body.get("team_name", "").strip()
        company_url = req_body.get("company_url", "#").strip()
        year_range = req_body.get("year_range", "").strip()
        description = req_body.get("description", "").strip()

        if not company_url:
            company_url = get_company_url(company)

        # If the description is missing, generate it using OpenAI
        if not description:
            description = generate_ai_job_description(job_title, company, team_name, tec)

        if not all([job_title, company, team_name, year_range, description]):
            res.set(func.HttpResponse(json.dumps({"error": "Missing required fields for work experience (title, company, team_name, year_range, description)"}), status_code=400, mimetype="application/json"))
            return

        # Generate new work experience HTML snippet
        new_content_html = f"""
        <div class="item">
            <h3 class="title">{job_title} - <span class="place"><a href="{company_url}" target="_blank">{company}</a></span> <span class="year">({year_range})</span></h3>
            <p>{description}</p>
        </div>
        """

        # Update "Work Experience" section
        update_result = update_index_html(new_content_html, "experience section")

    else:
        print()
        res.set(func.HttpResponse(json.dumps({"error": "Invalid type. Must be 'project' or 'work'."}), status_code=400, mimetype="application/json"))
        return

    res.set(func.HttpResponse(json.dumps(update_result), mimetype="application/json", status_code=200))
    return
