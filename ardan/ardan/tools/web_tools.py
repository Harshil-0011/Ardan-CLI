import httpx
from bs4 import BeautifulSoup
from .file_tools import ToolResult

def search_web(query: str) -> ToolResult:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        url = "https://duckduckgo.com/html/"
        params = {"q": query}

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, headers=headers, params=params)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("div", class_="result__body", limit=5)

        if not results:
            return ToolResult(True, "No results found for query.")

        output = []
        for res in results:
            title_tag = res.find("a", class_="result__a")
            snippet_tag = res.find("a", class_="result__snippet")

            if title_tag and snippet_tag:
                title = title_tag.get_text()
                snippet = snippet_tag.get_text()
                output.append(f"Title: {title}\nSnippet: {snippet}\n---")

        return ToolResult(True, "\n".join(output))
    except Exception as e:
        return ToolResult(False, "", str(e))

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
            return ToolResult(True, text[:10000]) # Limit output
        else:
            return ToolResult(True, response.text[:10000])
    except Exception as e:
        return ToolResult(False, "", str(e))
