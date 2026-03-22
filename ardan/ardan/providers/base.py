from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Dict, Any, Optional, Union, Generator
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
        pass

    @abstractmethod
    def list_models(self) -> List[ModelInfo]:
        pass

    @abstractmethod
    def health_check(self) -> HealthStatus:
        pass
