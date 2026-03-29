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
    """Attempt generation with failover logic through configured providers."""
    try:
        async for chunk in primary_provider.generate(messages, config):
            yield chunk
    except Exception as e:
        if not settings.get("agent", "auto_failover"):
            raise e

        # Get list of other providers that might have keys set
        providers_to_try = ["anthropic", "openai", "google", "groq", "mistral", "openrouter", "ollama"]
        tried = {primary_provider.name}

        for p_name in providers_to_try:
            if p_name in tried:
                continue

            # Only try if it's ollama or we have a key
            if p_name != "ollama" and not credentials_manager.get(p_name):
                continue

            try:
                fallback = get_provider_instance(p_name, settings)
                async for chunk in fallback.generate(messages, config):
                    yield chunk
                return # Success
            except Exception:
                tried.add(p_name)
                continue

        # If all fallback failed, raise original error
        raise e
