import asyncio
from typing import AsyncIterator, List, Optional
from ardan.providers.base import BaseProvider, ArdanProviderError
from ardan.agent.messages import Message, GenerationConfig, ModelInfo, HealthStatus
from ardan.ollama.client import OllamaClient


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
        self.client = OllamaClient(base_url=base_url)

    async def generate(
        self, messages: List[Message], config: GenerationConfig
    ) -> AsyncIterator[str]:
        formatted_messages = [{"role": m.role, "content": m.content} for m in messages]
        try:
            async for chunk in self.client.generate(
                model=self.default_model,
                messages=formatted_messages,
                stream=config.stream,
                temperature=config.temperature,
                num_ctx=8192
            ):
                yield chunk
        except Exception as e:
            raise ArdanProviderError(str(e), self.name)

    async def list_models(self) -> List[ModelInfo]:
        try:
            data = await self.client.list_models()
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
            data = await self.client.list_models()
            return HealthStatus("healthy", "Ollama is reachable.")
        except Exception as e:
            return HealthStatus("unhealthy", f"Ollama unreachable: {str(e)}")
