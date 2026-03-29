import httpx
from bs4 import BeautifulSoup
from .file_tools import ToolResult


def fetch_url(url: str) -> ToolResult:
    """Fetch the content of a URL and return it as plain text."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()

        # If it's HTML, try to extract text
        if "text/html" in response.headers.get("Content-Type", ""):
            soup = BeautifulSoup(response.text, "html.parser")
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text(separator=" ")
            # break into lines and remove leading and trailing whitespace
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = "\n".join(chunk for chunk in chunks if chunk)
            return ToolResult(True, text[:10000])  # Limit output
        else:
            return ToolResult(True, response.text[:10000])
    except Exception as e:
        return ToolResult(False, "", str(e))


def search_web(query: str) -> ToolResult:
    """Scrape DuckDuckGo results."""
    try:
        url = "https://duckduckgo.com/html/"
        params = {"q": query}
        headers = {"User-Agent": "Mozilla/5.0"}
        with httpx.Client() as client:
            res = client.get(url, params=params, headers=headers)
            res.raise_for_status()
            # Simple scrape
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(res.text, "html.parser")
            results = [a.text for a in soup.select(".result__a")[:5]]
            return ToolResult(True, "\n".join(results), "")
    except Exception as e:
        return ToolResult(False, "", str(e))
