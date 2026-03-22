import json
import httpx
import time
from typing import List, AsyncIterator, Dict, Any, Optional
from ardan.providers.base import BaseProvider
from ardan.agent.messages import Message, GenerationConfig, ModelInfo, HealthStatus

class OllamaProvider(BaseProvider):
    name = "ollama"
    display_name = "Ollama"
    requires_api_key = False
    supported_models = ["codellama:13b", "llama3", "mistral", "llava"]
    default_model = "codellama:13b"

    def __init__(self, api_key: Optional[str] = None, base_url: str = "http://localhost:11434"):
        super().__init__(api_key, base_url)
        self.timeout = 120.0

    async def generate(self, messages: List[Message], config: GenerationConfig) -> AsyncIterator[str]:
        # Refactor existing Ollama logic into unified message format
        # Map Ardan Message -> Ollama chat format
        ollama_messages = []
        for m in messages:
             msg = {"role": m.role, "content": m.content}
             if m.images:
                  msg["images"] = m.images
             ollama_messages.append(msg)

        payload = {
            "model": self.default_model,
            "messages": ollama_messages,
            "stream": config.stream,
            "options": {
                "temperature": config.temperature,
                "num_ctx": 8192
            }
        }

        if not config.stream:
             async with httpx.AsyncClient(timeout=self.timeout) as client:
                  response = await client.post(f"{self.base_url}/api/chat", json=payload)
                  response.raise_for_status()
                  yield response.json().get("message", {}).get("content", "")
             return

        max_retries = 3
        retry_delay = 1.0
        for i in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            if not line: continue
                            chunk = json.loads(line)
                            if "message" in chunk and "content" in chunk["message"]:
                                yield chunk["message"]["content"]
                            if chunk.get("done"): return
                return
            except (httpx.ConnectError, httpx.HTTPStatusError, httpx.TimeoutException) as e:
                if i == max_retries - 1: raise e
                await asyncio.sleep(retry_delay)
                retry_delay *= 2

    def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.request(method, f"{self.base_url}{endpoint}", **kwargs)
            response.raise_for_status()
            return response

    def list_models(self) -> List[ModelInfo]:
        try:
             response = self._request("GET", "/api/tags")
             models = response.json().get("models", [])
             return [ModelInfo(id=m["name"], name=m["name"], provider="ollama", context_window=8192) for m in models]
        except:
             return []

    def health_check(self) -> HealthStatus:
        try:
             self._request("GET", "/api/tags")
             return HealthStatus("healthy", "Ollama is running.")
        except Exception as e:
             return HealthStatus("unhealthy", f"Ollama unreachable: {str(e)}")
