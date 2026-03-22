import os
from typing import Dict, Any, Type, Optional
from ardan.providers.base import BaseProvider
from ardan.providers.ollama import OllamaProvider
from ardan.providers.anthropic import AnthropicProvider
from ardan.providers.google import GoogleProvider
from ardan.providers.openai import OpenAIProvider
from ardan.providers.mistral import MistralProvider
from ardan.providers.groq import GroqProvider
from ardan.providers.openrouter import OpenRouterProvider

PROVIDERS: Dict[str, Type[BaseProvider]] = {
    "ollama":      OllamaProvider,
    "anthropic":   AnthropicProvider,
    "google":      GoogleProvider,
    "openai":      OpenAIProvider,
    "mistral":     MistralProvider,
    "groq":        GroqProvider,
    "openrouter":  OpenRouterProvider,
}

ALIASES = {
    "claude": "anthropic",
    "gemini": "google",
    "gpt":    "openai",
    "fast":   "groq"
}

def get_provider(name: str, api_key: Optional[str] = None, base_url: Optional[str] = None) -> BaseProvider:
    name = name.lower()
    name = ALIASES.get(name, name)

    if name not in PROVIDERS:
        raise ValueError(f"Provider '{name}' not found. Available: {', '.join(PROVIDERS.keys())}")

    provider_cls = PROVIDERS[name]
    return provider_cls(api_key=api_key, base_url=base_url)

def detect_active_provider(cli_flag: Optional[str] = None, env_var: Optional[str] = None, config_val: Optional[str] = None) -> str:
    if cli_flag: return cli_flag
    if env_var: return env_var
    if config_val: return config_val
    return "ollama"
