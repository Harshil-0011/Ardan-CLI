import time
from typing import List, AsyncIterator, Optional, Any, Dict
from ardan.providers.base import BaseProvider
from ardan.agent.messages import Message, GenerationConfig, ModelInfo, HealthStatus

try:
    import groq
except ImportError:
    groq = None

class GroqProvider(BaseProvider):
    name = "groq"
    display_name = "Groq"
    requires_api_key = True
    supported_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]
    default_model = "llama-3.3-70b-versatile"

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        self.client = None
        if groq:
             self.client = groq.Groq(api_key=api_key)

    async def generate(self, messages: List[Message], config: GenerationConfig) -> AsyncIterator[str]:
        if not self.client:
             raise ImportError("Groq SDK not installed. Run: pip install ardan[groq]")

        async_client = groq.AsyncGroq(api_key=self.api_key)

        user_messages = [{"role": m.role, "content": m.content} for m in messages]

        start_time = time.time()
        total_tokens = 0

        if config.stream:
             response = await async_client.chat.completions.create(
                  model=self.default_model,
                  messages=user_messages,
                  temperature=config.temperature,
                  max_tokens=config.max_tokens,
                  top_p=config.top_p,
                  stream=True
             )
             async for chunk in response:
                  if chunk.choices and chunk.choices[0].delta.content:
                       yield chunk.choices[0].delta.content
        else:
             response = await async_client.chat.completions.create(
                  model=self.default_model,
                  messages=user_messages,
                  temperature=config.temperature,
                  max_tokens=config.max_tokens,
                  top_p=config.top_p,
                  stream=False
             )
             yield response.choices[0].message.content

    def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(id="llama-3.3-70b-versatile", name="Llama 3.3 70b Versatile", provider="groq", context_window=128000),
            ModelInfo(id="llama-3.1-8b-instant", name="Llama 3.1 8b Instant", provider="groq", context_window=128000),
            ModelInfo(id="mixtral-8x7b-32768", name="Mixtral 8x7b 32768", provider="groq", context_window=32768)
        ]

    def health_check(self) -> HealthStatus:
        if not self.client:
             return HealthStatus("unhealthy", "Groq SDK not installed.")
        return HealthStatus("healthy", "Groq provider ready.")
