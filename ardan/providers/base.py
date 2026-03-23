from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Optional
from ardan.agent.messages import Message, GenerationConfig, ModelInfo, HealthStatus

class BaseProvider(ABC):
    name: str
    display_name: str
    requires_api_key: bool
    supported_models: List[str]
    default_model: str

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    async def generate(self, messages: List[Message], config: GenerationConfig) -> AsyncIterator[str]:
        """Perform asynchronous streaming generation."""
        pass

    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """Return a list of supported models."""
        pass

    @abstractmethod
    async def health_check(self) -> HealthStatus:
        """Check if the provider is reachable and correctly configured."""
        pass

class ArdanProviderError(Exception):
    """Custom exception for provider-specific errors."""
    def __init__(self, message: str, provider: str):
        self.provider = provider
        super().__init__(f"[{provider}] {message}")
