import time
from typing import List, AsyncIterator, Optional, Any, Dict
from ardan.providers.base import BaseProvider
from ardan.agent.messages import Message, GenerationConfig, ModelInfo, HealthStatus

try:
    import mistralai
except ImportError:
    mistralai = None

class MistralProvider(BaseProvider):
    name = "mistral"
    display_name = "Mistral"
    requires_api_key = True
    supported_models = ["codestral-latest", "mistral-large-latest", "mistral-medium", "open-mixtral-8x22b"]
    default_model = "codestral-latest"

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        self.client = None
        if mistralai:
             self.client = mistralai.Mistral(api_key=api_key)

    async def generate(self, messages: List[Message], config: GenerationConfig) -> AsyncIterator[str]:
        if not self.client:
             raise ImportError("Mistral SDK not installed. Run: pip install ardan[mistral]")

        user_messages = [{"role": m.role, "content": m.content} for m in messages]

        if config.stream:
             response = await self.client.chat.stream_async(
                  model=self.default_model,
                  messages=user_messages,
                  temperature=config.temperature,
                  max_tokens=config.max_tokens,
                  top_p=config.top_p
             )
             async for chunk in response:
                  if chunk.data.choices[0].delta.content:
                       yield chunk.data.choices[0].delta.content
        else:
             response = await self.client.chat.complete_async(
                  model=self.default_model,
                  messages=user_messages,
                  temperature=config.temperature,
                  max_tokens=config.max_tokens,
                  top_p=config.top_p
             )
             yield response.choices[0].message.content

    def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(id="codestral-latest", name="Codestral Latest", provider="mistral", context_window=32000),
            ModelInfo(id="mistral-large-latest", name="Mistral Large Latest", provider="mistral", context_window=32000),
            ModelInfo(id="mistral-medium", name="Mistral Medium", provider="mistral", context_window=32000)
        ]

    def health_check(self) -> HealthStatus:
        if not self.client:
             return HealthStatus("unhealthy", "Mistral SDK not installed.")
        return HealthStatus("healthy", "Mistral provider ready.")
