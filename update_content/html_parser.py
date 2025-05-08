# File: update_content/html_parser.py
import os
import requests
import base64
from bs4 import BeautifulSoup

def read_portfolio_html(user_id: str) -> str:
    """
    Fetches the portfolio HTML (index.html) from the GitHub repository.
    """
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO", "veeravn/portfolio-ai")
    path = "index.html"
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    content_b64 = resp.json().get("content", "")
    return base64.b64decode(content_b64).decode()

def insert_project(html: str, project: dict) -> str:
    """
    Inserts a new project card into the #projects section of the HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    section = soup.find(id="projects")
    if section is None:
        raise ValueError("Projects section not found in HTML.")

    card = soup.new_tag("div", **{"class": "project-card"})
    title = soup.new_tag("h3")
    title.string = project.get("title", "")
    desc = soup.new_tag("p")
    desc.string = project.get("description", "")
    card.append(title)
    card.append(desc)

    link = project.get("link")
    if link:
        a = soup.new_tag("a", href=link)
        a.string = "View Project"
        card.append(a)

    section.append(card)
    return str(soup)

def insert_experience(html: str, experience: dict) -> str:
    """
    Inserts a new work experience entry into the #experience section of the HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    section = soup.find(id="experience")
    if section is None:
        raise ValueError("Experience section not found in HTML.")

    entry = soup.new_tag("div", **{"class": "experience-entry"})
    header = soup.new_tag("h3")
    header.string = f"{experience.get('role', '')} at {experience.get('company', '')}"
    dates = soup.new_tag("span")
    start = experience.get("start_date", "")
    end = experience.get("end_date", "Present")
    dates.string = f"{start} - {end}"
    desc = soup.new_tag("p")
    desc.string = experience.get("description", "")

    entry.append(header)
    entry.append(dates)
    entry.append(desc)
    section.append(entry)
    return str(soup)
