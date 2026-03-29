from typing import Dict, Any, Type, Optional, List
from ardan.providers.base import BaseProvider
from ardan.providers.ollama import OllamaProvider
from ardan.providers.anthropic import AnthropicProvider
from ardan.providers.google import GoogleProvider
from ardan.providers.openai import OpenAIProvider
from ardan.providers.mistral import MistralProvider
from ardan.providers.groq import GroqProvider
from ardan.providers.openrouter import OpenRouterProvider
from ardan.config.credentials import credentials_manager

PROVIDERS: Dict[str, Type[BaseProvider]] = {
    "ollama": OllamaProvider,
    "anthropic": AnthropicProvider,
    "google": GoogleProvider,
    "openai": OpenAIProvider,
    "mistral": MistralProvider,
    "groq": GroqProvider,
    "openrouter": OpenRouterProvider,
}

ALIASES = {"claude": "anthropic", "gemini": "google", "gpt": "openai", "fast": "groq"}


def get_provider_instance(name: str, settings: Any) -> BaseProvider:
    name = name.lower()
    name = ALIASES.get(name, name)

    if name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {name}")

    cls = PROVIDERS[name]
    api_key = credentials_manager.get(name)
    base_url = settings.get("providers", {}).get(name, {}).get("base_url")

    return cls(api_key=api_key, base_url=base_url)


def detect_active_provider(
    cli_flag: Optional[str], env_var: Optional[str], config_val: str
) -> str:
    if cli_flag:
        return cli_flag
    if env_var:
        return env_var
    return config_val or "ollama"


async def failover_generate(
    messages: List[Any], config: Any, primary_provider: BaseProvider, settings: Any
):
    """Attempt generation with failover logic."""
    try:
        async for chunk in primary_provider.generate(messages, config):
            yield chunk
    except Exception as e:
        if settings.get("agent", "auto_failover") and primary_provider.name != "ollama":
            # Simple failover to ollama for now
            fallback = get_provider_instance("ollama", settings)
            async for chunk in fallback.generate(messages, config):
                yield chunk
        else:
            raise e
