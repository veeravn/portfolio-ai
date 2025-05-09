import os
import base64
import requests

def commit_html(path: str, content: str) -> dict:
    """
    Commit a file to GitHub via Contents API.
    """
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO", "veeravn/portfolio-ai")
    api_url = f"https://api.github.com/repos/{repo}/contents/{path}"

    # Check if file exists to get SHA
    resp = requests.get(api_url, headers={"Authorization": f"token {token}"})
    sha = resp.json().get("sha")

    data = {
        "message": "Automated update via AI agent",
        "content": base64.b64encode(content.encode()).decode(),
        "branch": "master"
    }
    if sha:
        data["sha"] = sha
    put_resp = requests.put(
        api_url,
        json=data,
        headers={"Authorization": f"token {token}"}
    )
    put_resp.raise_for_status()
    return put_resp.json()