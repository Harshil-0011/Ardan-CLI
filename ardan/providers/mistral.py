import os
import asyncio
from typing import AsyncIterator, List, Optional
from ardan.providers.base import BaseProvider, ArdanProviderError
from ardan.agent.messages import Message, GenerationConfig, ModelInfo, HealthStatus

try:
    import mistralai
except ImportError:
    mistralai = None

class MistralProvider(BaseProvider):
    name = "mistral"
    display_name = "Mistral"
    requires_api_key = True
    supported_models = ["codestral-latest", "mistral-large-latest", "mistral-medium-latest", "open-mixtral-8x22b"]
    default_model = "codestral-latest"

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        self.client = mistralai.Mistral(api_key=api_key) if mistralai and api_key else None

    async def generate(self, messages: List[Message], config: GenerationConfig) -> AsyncIterator[str]:
        if not self.client:
            raise ArdanProviderError("Mistral SDK not installed or API key missing. Install with: pip install ardan[mistral]", self.name)

        try:
            response = await self.client.chat.stream_async(
                model=self.default_model,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
            )
            async for chunk in response:
                if chunk.data.choices[0].delta.content:
                    yield chunk.data.choices[0].delta.content
        except Exception as e:
            raise ArdanProviderError(str(e), self.name)

    async def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(id="codestral-latest", name="Codestral Latest", provider=self.name, context_window=32000, pricing_per_1m_tokens=1.0, strength="Best dedicated code model"),
        ]

    async def health_check(self) -> HealthStatus:
        if not mistralai: return HealthStatus("unhealthy", "Mistral SDK not installed.")
        if not self.api_key: return HealthStatus("unhealthy", "API key missing.")
        return HealthStatus("healthy", "Mistral configured.")
