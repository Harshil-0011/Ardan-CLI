from dataclasses import dataclass, field
from typing import Literal, Optional, List, Dict, Any

@dataclass
class Message:
    role: Literal["system", "user", "assistant"]
    content: str
    provider_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GenerationConfig:
    temperature: float = 0.2
    max_tokens: int = 8096
    stream: bool = True
    top_p: float = 1.0
    stop_sequences: List[str] = field(default_factory=list)
    thinking: bool = False # For Claude extended thinking

@dataclass
class ModelInfo:
    id: str
    name: str
    provider: str
    context_window: int
    pricing_per_1m_tokens: Optional[float] = None
    strength: str = ""

@dataclass
class HealthStatus:
    status: Literal["healthy", "unhealthy"]
    message: str
