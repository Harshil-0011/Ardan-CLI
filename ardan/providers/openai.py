from typing import AsyncIterator, List, Optional
from ardan.providers.base import BaseProvider, ArdanProviderError
from ardan.agent.messages import Message, GenerationConfig, ModelInfo, HealthStatus

try:
    import openai
except ImportError:
    openai = None


class OpenAIProvider(BaseProvider):
    name = "openai"
    display_name = "OpenAI"
    requires_api_key = True
    supported_models = [
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4o",
        "gpt-4o-mini",
        "o3",
        "o4-mini",
    ]
    default_model = "gpt-4.1"

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        self.client = (
            openai.AsyncOpenAI(api_key=api_key, base_url=base_url)
            if openai and api_key
            else None
        )

    async def generate(
        self, messages: List[Message], config: GenerationConfig
    ) -> AsyncIterator[str]:
        if not self.client:
            raise ArdanProviderError(
                "OpenAI SDK not installed or API key missing. Install with: pip install ardan[openai]",
                self.name,
            )

        try:
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                stream=True,
            )
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise ArdanProviderError(str(e), self.name)

    async def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(
                id="gpt-4.1",
                name="GPT-4.1",
                provider=self.name,
                context_window=128000,
                pricing_per_1m_tokens=2.0,
                strength="Best tool use accuracy",
            ),
            ModelInfo(
                id="o3",
                name="OpenAI o3",
                provider=self.name,
                context_window=200000,
                pricing_per_1m_tokens=10.0,
                strength="Best deep reasoning",
            ),
        ]

    async def health_check(self) -> HealthStatus:
        if not openai:
            return HealthStatus("unhealthy", "OpenAI SDK not installed.")
        if not self.api_key:
            return HealthStatus("unhealthy", "API key missing.")
        return HealthStatus("healthy", "OpenAI configured.")
