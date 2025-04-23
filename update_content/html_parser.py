# File: update_content/html_parser.py
def parse_html(html: str) -> dict:
    """
    Very simple HTML parser: returns target path and cleaned content.
    """
    # For more complex sites, integrate BeautifulSoup or similar.
    return {"path": "index.html", "content": html.strip()}