import time
import json
from typing import List, AsyncIterator, Optional, Any, Dict
from ardan.providers.base import BaseProvider
from ardan.agent.messages import Message, GenerationConfig, ModelInfo, HealthStatus

try:
    import anthropic
except ImportError:
    anthropic = None

class AnthropicProvider(BaseProvider):
    name = "anthropic"
    display_name = "Anthropic"
    requires_api_key = True
    supported_models = ["claude-3-5-sonnet-latest", "claude-3-5-haiku-latest", "claude-3-opus-20240229"]
    default_model = "claude-3-5-sonnet-latest"

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        self.client = None
        if anthropic:
            self.client = anthropic.Anthropic(api_key=api_key)

    async def generate(self, messages: List[Message], config: GenerationConfig) -> AsyncIterator[str]:
        if not self.client:
             raise ImportError("Anthropic SDK not installed. Run: pip install ardan[anthropic]")

        async_client = anthropic.AsyncAnthropic(api_key=self.api_key)

        system_prompt = ""
        user_messages = []
        for m in messages:
             if m.role == "system":
                  system_prompt += m.content + "\n"
             else:
                  # Anthropic role: user, assistant
                  role = m.role if m.role in ["user", "assistant"] else "user"
                  msg_content = []
                  if m.images:
                       for img in m.images:
                            msg_content.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": img
                                }
                            })
                  msg_content.append({"type": "text", "text": m.content})
                  user_messages.append({"role": role, "content": msg_content})

        kwargs = {
            "model": self.default_model,
            "max_tokens": config.max_tokens,
            "messages": user_messages,
            "system": system_prompt,
            "temperature": config.temperature,
            "stream": config.stream
        }

        if config.thinking:
             kwargs["thinking"] = {"type": "enabled", "budget_tokens": 1024}

        if not config.stream:
             response = await async_client.messages.create(**kwargs)
             yield response.content[0].text
             return

        async with async_client.messages.stream(**kwargs) as stream:
             async for text in stream.text_stream:
                  yield text

    def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(id="claude-3-5-sonnet-latest", name="Claude 3.5 Sonnet", provider="anthropic", context_window=200000),
            ModelInfo(id="claude-3-5-haiku-latest", name="Claude 3.5 Haiku", provider="anthropic", context_window=200000),
            ModelInfo(id="claude-3-opus-20240229", name="Claude 3 Opus", provider="anthropic", context_window=200000)
        ]

    def health_check(self) -> HealthStatus:
        if not self.client:
             return HealthStatus("unhealthy", "Anthropic SDK not installed.")
        return HealthStatus("healthy", "Anthropic provider ready.")
