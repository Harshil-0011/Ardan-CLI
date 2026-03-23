import time
from typing import AsyncIterator, List, Optional
from ardan.providers.base import BaseProvider, ArdanProviderError
from ardan.agent.messages import Message, GenerationConfig, ModelInfo, HealthStatus

try:
    import groq
except ImportError:
    groq = None


class GroqProvider(BaseProvider):
    name = "groq"
    display_name = "Groq"
    requires_api_key = True
    supported_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ]
    default_model = "llama-3.3-70b-versatile"

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        self.client = groq.AsyncGroq(api_key=api_key) if groq and api_key else None

    async def generate(
        self, messages: List[Message], config: GenerationConfig
    ) -> AsyncIterator[str]:
        if not self.client:
            raise ArdanProviderError(
                "Groq SDK not installed or API key missing. Install with: pip install ardan[groq]",
                self.name,
            )

        try:
            start_time = time.time()
            token_count = 0
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
                    content = chunk.choices[0].delta.content
                    token_count += len(content.split())  # Rough estimate
                    yield content

            elapsed = time.time() - start_time
            if elapsed > 0:
                tps = token_count / elapsed
                yield f"\n[TPS: {tps:.2f}]\n"
        except Exception as e:
            raise ArdanProviderError(str(e), self.name)

    async def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(
                id="llama-3.3-70b-versatile",
                name="Llama 3.3 70b",
                provider=self.name,
                context_window=128000,
                pricing_per_1m_tokens=0.0,
                strength="Fastest inference alive",
            ),
        ]

    async def health_check(self) -> HealthStatus:
        if not groq:
            return HealthStatus("unhealthy", "Groq SDK not installed.")
        if not self.api_key:
            return HealthStatus("unhealthy", "API key missing.")
        return HealthStatus("healthy", "Groq configured.")
