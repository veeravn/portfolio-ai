import json
from update_content.html_parser import parse_html
from github_helper import commit_html

async def send_update_request(user_id: str, html_content: str) -> dict:
    parsed = parse_html(html_content=html_content)
    result = commit_html(path=parsed["path"], content=parsed["content"])
    return {"status": "committed", "details": result}