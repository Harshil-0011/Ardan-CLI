from typing import AsyncIterator, List, Optional
from ardan.providers.base import BaseProvider, ArdanProviderError
from ardan.agent.messages import Message, GenerationConfig, ModelInfo, HealthStatus

try:
    import anthropic
except ImportError:
    anthropic = None


class AnthropicProvider(BaseProvider):
    name = "anthropic"
    display_name = "Anthropic"
    requires_api_key = True
    supported_models = ["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5"]
    default_model = "claude-sonnet-4-6"

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        self.client = (
            anthropic.AsyncAnthropic(api_key=api_key) if anthropic and api_key else None
        )

    async def generate(
        self, messages: List[Message], config: GenerationConfig
    ) -> AsyncIterator[str]:
        if not self.client:
            raise ArdanProviderError(
                "Anthropic SDK not installed or API key missing. Install with: pip install ardan[anthropic]",
                self.name,
            )

        system_prompt = next((m.content for m in messages if m.role == "system"), "")
        anthropic_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role != "system"
        ]

        kwargs = {
            "model": self.default_model,
            "max_tokens": config.max_tokens,
            "messages": anthropic_messages,
            "system": system_prompt,
            "temperature": config.temperature,
            "stream": True,
        }

        if config.thinking and "opus" in self.default_model:
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": 1024}

        try:
            async with self.client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise ArdanProviderError(str(e), self.name)

    async def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(
                id="claude-sonnet-4-6",
                name="Claude 4.6 Sonnet",
                provider=self.name,
                context_window=200000,
                pricing_per_1m_tokens=3.0,
                strength="Best at complex reasoning",
            ),
            ModelInfo(
                id="claude-opus-4-6",
                name="Claude 4.6 Opus",
                provider=self.name,
                context_window=200000,
                pricing_per_1m_tokens=15.0,
                strength="Most powerful overall",
            ),
        ]

    async def health_check(self) -> HealthStatus:
        if not anthropic:
            return HealthStatus("unhealthy", "Anthropic SDK not installed.")
        if not self.api_key:
            return HealthStatus("unhealthy", "API key missing.")
        return HealthStatus("healthy", "Anthropic configured.")
