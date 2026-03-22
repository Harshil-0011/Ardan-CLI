import httpx
import json
import time
from typing import Any, Dict, List, Optional, Generator, Union

class OllamaClient:
    def __init__(self, base_url: str, model: str, temperature: float = 0.2, num_ctx: int = 8192):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.num_ctx = num_ctx
        self.timeout = 120.0

    def _request_with_retry(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        max_retries = 3
        retry_delay = 1.0
        for i in range(max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.request(method, f"{self.base_url}{endpoint}", **kwargs)
                    response.raise_for_status()
                    return response
            except (httpx.ConnectError, httpx.HTTPStatusError, httpx.TimeoutException) as e:
                if i == max_retries - 1:
                    raise e
                time.sleep(retry_delay)
                retry_delay *= 2
        raise Exception("Failed to connect to Ollama after multiple retries.")

    def generate(self, prompt: str, system: Optional[str] = None, stream: bool = True) -> Union[str, Generator[str, None, None]]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": stream,
            "options": {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx
            }
        }

        if stream:
            return self._stream_response("/api/generate", payload)
        else:
            response = self._request_with_retry("POST", "/api/generate", json=payload)
            return response.json().get("response", "")

    def chat(self, messages: List[Dict[str, Any]], stream: bool = True) -> Union[str, Generator[str, None, None]]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx
            }
        }

        if stream:
            return self._stream_response("/api/chat", payload)
        else:
            response = self._request_with_retry("POST", "/api/chat", json=payload)
            return response.json().get("message", {}).get("content", "")

    def _stream_response(self, endpoint: str, payload: Dict[str, Any]) -> Generator[str, None, None]:
        max_retries = 3
        retry_delay = 1.0

        for i in range(max_retries):
            try:
                yield from self._do_stream(endpoint, payload)
                return
            except (httpx.ConnectError, httpx.HTTPStatusError, httpx.TimeoutException) as e:
                if i == max_retries - 1:
                    raise e
                time.sleep(retry_delay)
                retry_delay *= 2

    def _do_stream(self, endpoint: str, payload: Dict[str, Any]) -> Generator[str, None, None]:
        try:
            with httpx.stream("POST", f"{self.base_url}{endpoint}", json=payload, timeout=self.timeout) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
                        elif "message" in chunk and "content" in chunk["message"]:
                            yield chunk["message"]["content"]

                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
        except (httpx.ConnectError, httpx.HTTPStatusError) as e:
             raise Exception(f"Error connecting to Ollama: {str(e)}")

    def list_models(self) -> List[Dict[str, Any]]:
        response = self._request_with_retry("GET", "/api/tags")
        return response.json().get("models", [])
