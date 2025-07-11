# File: update_content/html_parser.py
import requests
import base64
from bs4 import BeautifulSoup
import logging as log
import re
from config.env import GITHUB_REPO, GITHUB_TOKEN

def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

def read_portfolio_html(user_id: str) -> str:
    """
    Fetches the portfolio HTML (index.html) from the GitHub repository.
    """
    token = GITHUB_TOKEN
    log.info(f"[read_portfolio_html] token: {token}")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is not set.")
    repo = GITHUB_REPO
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

def update_project(html: str, project: dict) -> str:
    """
    Update an existing project <div class="item"> by matching its title text,
    without assuming it’s wrapped in an <a>. If a new link is provided, wrap
    the title in an <a> (or update the existing one).
    """
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find("section", class_="projects section")
    if not container:
        raise ValueError("Could not find .projects container")

    for item in container.find_all("div", class_="item"):
        h3 = item.find("h3", class_="title")
        if not h3:
            continue

        # Full title text, stripping inner tags
        title_text = h3.get_text(separator=" ").strip()
        if title_text == project["title"]:
            # 1) Handle link update/wrap
            link = project.get("link")
            existing_a = h3.find("a")
            if link:
                if existing_a:
                    existing_a["href"] = link
                else:
                    # wrap the text node in a new <a>
                    new_a = soup.new_tag("a", href=link, target="_blank")
                    new_a.string = project["title"]
                    h3.string = ""            # clear old text
                    h3.append(new_a)

            # 2) Update description if present
            if project.get("description"):
                p = item.find("p", class_="summary")
                if p:
                    # clear all text in <p> and rebuild
                    p.clear()
                    p.append(project["description"])
                    p.append(soup.new_tag("br"))

                    # re-add tech stack if it exists
                    techs = project.get("technologies")
                    if techs:
                        b = soup.new_tag("b")
                        b.string = "Technology Stack -"
                        p.append(b)
                        p.append(" " + ", ".join(techs) + ".")

            # 3) If only techs changed
            if project.get("technologies") and not project.get("description"):
                p = item.find("p", class_="summary")
                if p:
                    # remove old tech section
                    for b in p.find_all("b"):
                        if "Technology Stack" in b.get_text():
                            # remove b and its siblings
                            for sib in list(b.next_siblings) + [b]:
                                sib.extract()
                    # append new one
                    p.append(soup.new_tag("br"))
                    b = soup.new_tag("b")
                    b.string = "Technology Stack -"
                    p.append(b)
                    p.append(" " + ", ".join(project["technologies"]) + ".")

            return str(soup)

    raise ValueError(f"No project titled '{project['title']}' found")

def update_experience(html: str, experience: dict) -> str:
    """
    Update an existing experience entry, matching on role (and optionally company),
    and patch only the provided fields. Now respects absence of 'description'.
    """
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find("section", class_="experience section")
    if not container:
        raise ValueError("Could not find experience container")

    role    = experience.get("role")
    company = experience.get("company")
    norm_role    = _normalize(role)    if role    else None
    norm_company = _normalize(company) if company else None
    # Notice: we do _not_ pull `description` yet

    candidates = []
    for item in container.find_all("div", class_="item"):
        h3 = item.find("h3", class_="title")
        if not h3:
            continue

        full_text = h3.get_text(separator=" ").replace("\n", " ")
        norm_text = _normalize(full_text)
        
        # Extract role and company fragments
        before_dash, _, after_dash = norm_text.partition(" - ")
        # strip off the year span at end for matching
        after_dash = re.sub(r"\(\d{4}\s*[–-]\s*\d{4}\)", "", after_dash).strip()

        # Check role match
        if norm_role and norm_role not in before_dash:
            continue
        # Check company match, if provided
        if norm_company and norm_company not in after_dash:
            continue

        candidates.append((item, before_dash, after_dash))

    if not candidates:
        crit = f"role='{role}'"
        if company:
            crit += f", company='{company}'"
        raise ValueError(f"No experience entry matching {crit} found")
    
    # If multiple candidates but only role was specified, pick the first
    item, _, _ = candidates[0]

    # 1) Update start/end dates if provided
    if "start_date" in experience or "end_date" in experience:
        year_span = item.find("span", class_="year")
        if year_span:
            start = experience.get("start_date", "") or year_span.text.strip("()").split(" - ")[0]
            end   = experience.get("end_date", "")   or "Present"
            year_span.string = f"({start} - {end})"

    # 2) Update description only if explicitly provided
    if "description" in experience:
        p = item.find("p")
        if p:
            # Remove existing text up to the <strong>
            for node in list(p.contents):
                if getattr(node, "name", "") == "strong":
                    break
                node.extract()
            # Insert new description + <br>
            p.insert(0, experience["description"])
            p.insert(1, soup.new_tag("br"))

    # 3) Update environment only if explicitly provided
    if "environment" in experience:
        p = item.find("p")
        strong = p.find("strong")
        if not strong:
            p.append(soup.new_tag("br"))
            strong = soup.new_tag("strong")
            strong.string = "Environment -"
            p.append(strong)
        # Remove old environment text
        for sib in list(strong.next_siblings):
            sib.extract()
        strong.insert_after(f" {', '.join(experience['environment'])}.")

    return str(soup)