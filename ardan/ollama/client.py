import json
import httpx
import asyncio
from typing import AsyncIterator, List, Optional, Dict, Any

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.timeout = httpx.Timeout(120.0, connect=10.0)

    async def generate(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = True,
        temperature: float = 0.2,
        num_ctx: int = 8192
    ) -> AsyncIterator[str]:
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_ctx": num_ctx
            },
        }

        max_retries = 3
        backoff = 1.0

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream(
                        "POST", f"{self.base_url}/api/chat", json=payload
                    ) as response:
                        if response.status_code != 200:
                            error_text = await response.aread()
                            raise Exception(f"Ollama error {response.status_code}: {error_text.decode()}")

                        async for line in response.aiter_lines():
                            if not line:
                                continue
                            chunk = json.loads(line)
                            if "message" in chunk and "content" in chunk["message"]:
                                yield chunk["message"]["content"]
                            if chunk.get("done"):
                                return
                return
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Ollama connection failed: {str(e)}")
                await asyncio.sleep(backoff)
                backoff *= 2

    async def list_models(self) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.json().get("models", [])
        except Exception:
            return []

    async def pull_model(self, model: str) -> AsyncIterator[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", f"{self.base_url}/api/pull", json={"name": model}) as response:
                async for line in response.aiter_lines():
                    if line:
                        yield json.loads(line)
