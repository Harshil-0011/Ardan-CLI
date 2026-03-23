import os
import asyncio
import httpx
from typing import AsyncIterator, List, Optional
from ardan.providers.base import BaseProvider, ArdanProviderError
from ardan.agent.messages import Message, GenerationConfig, ModelInfo, HealthStatus

try:
    import openai
except ImportError:
    openai = None

class OpenRouterProvider(BaseProvider):
    name = "openrouter"
    display_name = "OpenRouter"
    requires_api_key = True
    supported_models = ["deepseek/deepseek-coder-v2"]
    default_model = "deepseek/deepseek-coder-v2"

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://openrouter.ai/api/v1"):
        super().__init__(api_key, base_url)
        self.client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url) if openai and api_key else None

    async def generate(self, messages: List[Message], config: GenerationConfig) -> AsyncIterator[str]:
        if not self.client:
            raise ArdanProviderError("OpenRouter via OpenAI SDK not installed. Install with: pip install ardan[openai]", self.name)

        headers = {
            "HTTP-Referer": "https://github.com/ardan-cli",
            "X-Title": "Ardan"
        }

        try:
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                stream=True,
                extra_headers=headers
            )
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise ArdanProviderError(str(e), self.name)

    async def list_models(self) -> List[ModelInfo]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/models")
                data = response.json().get("data", [])
                return [ModelInfo(
                    id=m["id"],
                    name=m["name"],
                    provider=self.name,
                    context_window=m.get("context_length", 0),
                    pricing_per_1m_tokens=float(m.get("pricing", {}).get("prompt", 0)) * 1000000,
                    strength="Best open source coder"
                ) for m in data]
        except:
            return []

    async def health_check(self) -> HealthStatus:
        if not openai: return HealthStatus("unhealthy", "OpenAI SDK not installed.")
        if not self.api_key: return HealthStatus("unhealthy", "API key missing.")
        return HealthStatus("healthy", "OpenRouter configured.")
