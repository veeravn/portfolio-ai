import os
import json
from github import Github
from bs4 import BeautifulSoup

# GitHub Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "veeravn/veeravn.github.io"
INDEX_FILE_PATH = "index.html"

github_client = Github(GITHUB_TOKEN)

def fetch_index_html():
    """Fetch the latest version of index.html from GitHub"""
    repo = github_client.get_repo(GITHUB_REPO)
    file = repo.get_contents(INDEX_FILE_PATH)
    return file.decoded_content.decode("utf-8"), file.sha

def update_index_html(new_content_html, section_class):
    """Update index.html with new content in the specified section"""
    repo = github_client.get_repo(GITHUB_REPO)
    index_html, file_sha = fetch_index_html()

    soup = BeautifulSoup(index_html, "html.parser")

    section = soup.find("section", class_=section_class)
    if not section:
        return {"error": f"Could not find the '{section_class}' section in index.html"}

    section_inner_div = section.find("div", class_="section-inner")
    if not section_inner_div:
        return {"error": f"Could not find the 'section-inner' div in '{section_class}' section"}

    content_div = section_inner_div.find("div", class_="content")
    if not content_div:
        return {"error": f"Could not find the 'content' div inside the 'section-inner' div"}

    content_div.append(BeautifulSoup(new_content_html, "html.parser"))
    updated_html = soup.prettify(formatter=None)
    repo.update_file(INDEX_FILE_PATH, f"Updated {section_class} section", updated_html, file_sha)

    return {"success": f"{section_class} updated successfully"}
