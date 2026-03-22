import time
from typing import List, Generator, Optional, Any, Dict
from ardan.providers.base import BaseProvider
from ardan.agent.messages import Message, GenerationConfig, ModelInfo, HealthStatus

try:
    import google.generativeai as genai
except ImportError:
    genai = None

class GoogleProvider(BaseProvider):
    name = "google"
    display_name = "Google"
    requires_api_key = True
    supported_models = ["gemini-2.0-flash", "gemini-2.5-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
    default_model = "gemini-2.0-flash"

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        if genai:
             genai.configure(api_key=api_key)

    async def generate(self, messages: List[Message], config: GenerationConfig) -> AsyncIterator[str]:
        if not genai:
             raise ImportError("Google SDK not installed. Run: pip install ardan[google]")

        system_instruction = ""
        user_messages = []
        for m in messages:
             if m.role == "system":
                  system_instruction += m.content + "\n"
             else:
                  role = "user" if m.role == "user" else "model"
                  content = [m.content]
                  if m.images:
                       import base64
                       import PIL.Image
                       import io
                       for img in m.images:
                            content.append(PIL.Image.open(io.BytesIO(base64.b64decode(img))))
                  user_messages.append({"role": role, "parts": content})

        model = genai.GenerativeModel(
             model_name=self.default_model,
             system_instruction=system_instruction
        )

        gen_config = genai.types.GenerationConfig(
             temperature=config.temperature,
             max_output_tokens=config.max_tokens,
             top_p=config.top_p,
             stop_sequences=config.stop_sequences
        )

        if config.stream:
             response = await model.generate_content_async(user_messages, generation_config=gen_config, stream=True)
             async for chunk in response:
                  yield chunk.text
        else:
             response = await model.generate_content_async(user_messages, generation_config=gen_config)
             yield response.text

    def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(id="gemini-2.0-flash", name="Gemini 2.0 Flash", provider="google", context_window=1000000),
            ModelInfo(id="gemini-1.5-pro", name="Gemini 1.5 Pro", provider="google", context_window=2000000),
            ModelInfo(id="gemini-1.5-flash", name="Gemini 1.5 Flash", provider="google", context_window=1000000)
        ]

    def health_check(self) -> HealthStatus:
        if not genai:
             return HealthStatus("unhealthy", "Google SDK not installed.")
        return HealthStatus("healthy", "Google provider ready.")
