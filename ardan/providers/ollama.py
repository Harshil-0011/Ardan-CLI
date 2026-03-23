import json
import httpx
import asyncio
from typing import AsyncIterator, List, Optional
from ardan.providers.base import BaseProvider, ArdanProviderError
from ardan.agent.messages import Message, GenerationConfig, ModelInfo, HealthStatus


class OllamaProvider(BaseProvider):
    name = "ollama"
    display_name = "Ollama"
    requires_api_key = False
    supported_models = ["codellama:13b", "llama3", "mistral", "llava"]
    default_model = "codellama:13b"

    def __init__(
        self, api_key: Optional[str] = None, base_url: str = "http://localhost:11434"
    ):
        super().__init__(api_key, base_url)
        self.timeout = httpx.Timeout(120.0, connect=10.0)

    async def generate(
        self, messages: List[Message], config: GenerationConfig
    ) -> AsyncIterator[str]:
        payload = {
            "model": self.default_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": config.stream,
            "options": {"temperature": config.temperature, "num_ctx": 8192},
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
                            raise ArdanProviderError(
                                f"HTTP {response.status_code}", self.name
                            )

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
                    raise ArdanProviderError(f"Connection failed: {str(e)}", self.name)
                await asyncio.sleep(backoff)
                backoff *= 2

    async def list_models(self) -> List[ModelInfo]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                data = response.json().get("models", [])
                return [
                    ModelInfo(
                        id=m["name"],
                        name=m["name"],
                        provider=self.name,
                        context_window=8192,
                        strength="100% local no cost",
                    )
                    for m in data
                ]
        except Exception:
            return []

    async def health_check(self) -> HealthStatus:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.get(f"{self.base_url}/api/tags")
                return HealthStatus("healthy", "Ollama is reachable.")
        except Exception as e:
            return HealthStatus("unhealthy", f"Ollama unreachable: {str(e)}")
