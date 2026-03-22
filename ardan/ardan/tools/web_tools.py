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
