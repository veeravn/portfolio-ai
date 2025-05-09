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
    repo = os.getenv("GITHUB_REPO", "veeravn/veeravn.github.io")
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
    section = soup.find("section", class_="projects section")
    if section is None:
        raise ValueError("Projects section not found in HTML.")
    inner = section.find("div", class_="section-inner")
    content = inner.find("div", class_="content")

    # Build the new project item
    item = soup.new_tag("div", **{"class": "item"})

    # Title/link
    h3 = soup.new_tag("h3", **{"class": "title"})
    a = soup.new_tag(
        "a",
        href=project.get("link", "#"),
        target="_blank"
    )
    a.string = project["title"]
    h3.append(a)
    item.append(h3)

    # Summary paragraph
    p = soup.new_tag("p", **{"class": "summary"})
    # Description text
    p.append(project["description"])
    # Line break
    p.append(soup.new_tag("br"))
    # Bolded "Technology Stack -"
    b = soup.new_tag("b")
    b.string = "Technology Stack -"
    p.append(b)
    # Technologies list
    techs = project.get("technologies", [])
    if isinstance(techs, list):
        p.append(" " + ", ".join(techs))
    else:
        p.append(" " + str(techs))
    p.append(".")

    item.append(p)
    content.append(item)

    return str(soup)

def insert_experience(html: str, experience: dict) -> str:
    """
    Inserts a new work experience entry into the #experience section of the HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    section = soup.find("section", class_="experience section")
    if section is None:
        raise ValueError("Experience section not found in HTML.")
    inner = section.find("div", class_="section-inner")
    content = inner.find("div", class_="content")

    item = soup.new_tag("div", **{"class": "item"})
    title_h3 = soup.new_tag("h3", **{"class": "title"})
    title_h3.append(f"{experience['role']} - ")
    place_span = soup.new_tag("span", **{"class": "place"})
    a_tag = soup.new_tag(
        "a",
        href=experience.get("company_link", "#"),
        target="_blank"
    )
    a_tag.string = experience["company"]
    place_span.append(a_tag)
    title_h3.append(place_span)

    # Year span
    start = experience["start_date"]
    end = experience.get("end_date", "Present")
    year_span = soup.new_tag("span", **{"class": "year"})
    year_span.string = f"({start} - {end})"
    title_h3.append(year_span)

    item.append(title_h3)

    # Description paragraph
    desc_p = soup.new_tag("p")
    desc_p.append(experience["description"])
    desc_p.append(soup.new_tag("br"))

    # Environment line
    strong = soup.new_tag("strong")
    strong.string = "Environment -"
    desc_p.append(strong)

    # Append environment list
    envs = experience.get("environment", [])
    env_text = " " + ", ".join(envs) + "."
    desc_p.append(env_text)

    item.append(desc_p)
    
    content.append(item)
    return str(soup)
