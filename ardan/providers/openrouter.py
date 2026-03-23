import time
import httpx
from typing import List, AsyncIterator, Optional, Any, Dict
from ardan.providers.base import BaseProvider
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

    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        super().__init__(api_key, base_url)
        self.client = None
        if openai:
             self.client = openai.OpenAI(api_key=api_key, base_url=base_url)

    async def generate(self, messages: List[Message], config: GenerationConfig) -> AsyncIterator[str]:
        if not self.client:
             raise ImportError("OpenRouter via OpenAI SDK not installed. Run: pip install ardan[openai]")

        async_client = openai.AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

        user_messages = [{"role": m.role, "content": m.content} for m in messages]

        headers = {
             "HTTP-Referer": "https://github.com/ardan-cli",
             "X-Title": "Ardan"
        }

        if config.stream:
             response = await async_client.chat.completions.create(
                  model=self.default_model,
                  messages=user_messages,
                  temperature=config.temperature,
                  max_tokens=config.max_tokens,
                  top_p=config.top_p,
                  stream=True,
                  extra_headers=headers
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
                  stream=False,
                  extra_headers=headers
             )
             yield response.choices[0].message.content

    def list_models(self) -> List[ModelInfo]:
        try:
             response = httpx.get(f"{self.base_url}/models")
             data = response.json().get("data", [])
             return [ModelInfo(
                 id=m["id"],
                 name=m["name"],
                 provider="openrouter",
                 context_window=m.get("context_length", 0),
                 pricing_per_1k_tokens=float(m.get("pricing", {}).get("prompt", 0)) * 1000
             ) for m in data]
        except:
             return []

    def health_check(self) -> HealthStatus:
        if not self.client:
             return HealthStatus("unhealthy", "OpenRouter via OpenAI SDK not installed.")
        return HealthStatus("healthy", "OpenRouter provider ready.")
