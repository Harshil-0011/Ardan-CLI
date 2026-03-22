import time
from typing import List, Generator, Optional, Any, Dict
from ardan.providers.base import BaseProvider
from ardan.agent.messages import Message, GenerationConfig, ModelInfo, HealthStatus

try:
    import openai
except ImportError:
    openai = None

class OpenAIProvider(BaseProvider):
    name = "openai"
    display_name = "OpenAI"
    requires_api_key = True
    supported_models = ["gpt-4o", "gpt-4o-mini", "o3-mini", "o1-mini"]
    default_model = "gpt-4o"

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        self.client = None
        if openai:
             self.client = openai.OpenAI(api_key=api_key)

    async def generate(self, messages: List[Message], config: GenerationConfig) -> AsyncIterator[str]:
        if not self.client:
             raise ImportError("OpenAI SDK not installed. Run: pip install ardan[openai]")

        async_client = openai.AsyncOpenAI(api_key=self.api_key)

        user_messages = []
        for m in messages:
             content = [{"type": "text", "text": m.content}]
             if m.images:
                  for img in m.images:
                       content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img}"}
                       })
             user_messages.append({"role": m.role, "content": content})

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
            ModelInfo(id="gpt-4o", name="GPT-4o", provider="openai", context_window=128000),
            ModelInfo(id="gpt-4o-mini", name="GPT-4o Mini", provider="openai", context_window=128000),
            ModelInfo(id="o3-mini", name="o3-mini", provider="openai", context_window=128000),
            ModelInfo(id="o1-mini", name="o1-mini", provider="openai", context_window=128000)
        ]

    def health_check(self) -> HealthStatus:
        if not self.client:
             return HealthStatus("unhealthy", "OpenAI SDK not installed.")
        return HealthStatus("healthy", "OpenAI provider ready.")
