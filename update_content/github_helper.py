import os
import base64
import requests
from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter
from config.env import GITHUB_TOKEN, REPO_OWNER, REPO_NAME, API_BASE, GITHUB_BRANCH

FORMATTER = HTMLFormatter(indent=4)


def _get_file_sha(path: str) -> str | None:
    """
    Returns the SHA of the file at `path` on the target branch,
    or None if the file does not yet exist.
    """
    url = f"{API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    _headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept":        "application/vnd.github.v3+json"
    }
    resp = requests.get(url, params={"ref": GITHUB_BRANCH}, headers=_headers)
    if resp.status_code == 200:
        return resp.json().get("sha")
    if resp.status_code == 404:
        return None
    resp.raise_for_status()

def commit_html(content: str, section: str) -> dict:
    """
    Commits the updated HTML content to veeravn/veeravn.github.io on the master branch.
    Assumes the site structure has a folder per section under the repo root, e.g.:
      projects/index.html
      experience/index.html
    """
    # Path within the repo to update
    path = f"index.html"
    sha = _get_file_sha(path)

    url = f"{API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"

    # Prettify the HTML for cleaner formatting
    pretty_html = BeautifulSoup(content, "html.parser").prettify(formatter=FORMATTER)

    # GitHub expects base64-encoded content
    b64_content = base64.b64encode(pretty_html.encode("utf-8")).decode("utf-8")

    payload = {
        "message": f"Agent update to {section} section",
        "content": b64_content,
        "branch":  GITHUB_BRANCH,
    }
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept":        "application/vnd.github.v3+json"
    }
    if sha:
        payload["sha"] = sha
    
    
    resp = requests.put(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()