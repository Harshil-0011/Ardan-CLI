import os
import yaml
from pathlib import Path
from typing import Any, Dict

class Settings:
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Look for config.yaml in the project root relative to this file
            base_dir = Path(__file__).parent.parent.parent
            self.config_path = str(base_dir / "config.yaml")
        else:
            self.config_path = config_path
        self.config = self._load_config()
        self._override_from_env()

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f) or {}
        return {}

    def _override_from_env(self):
        # Env var override for ollama
        if "ARDAN_OLLAMA_BASE_URL" in os.environ:
            self.config.setdefault("ollama", {})["base_url"] = os.getenv("ARDAN_OLLAMA_BASE_URL")
        if "ARDAN_MODEL" in os.environ:
            self.config.setdefault("ollama", {})["model"] = os.getenv("ARDAN_MODEL")
        if "ARDAN_TEMPERATURE" in os.environ:
            self.config.setdefault("ollama", {})["temperature"] = float(os.getenv("ARDAN_TEMPERATURE"))
        if "ARDAN_NUM_CTX" in os.environ:
            self.config.setdefault("ollama", {})["num_ctx"] = int(os.getenv("ARDAN_NUM_CTX"))

        # Env var override for agent
        if "ARDAN_MAX_STEPS" in os.environ:
            self.config.setdefault("agent", {})["max_steps"] = int(os.getenv("ARDAN_MAX_STEPS"))
        if "ARDAN_AUTO_CONFIRM" in os.environ:
            self.config.setdefault("agent", {})["auto_confirm"] = os.getenv("ARDAN_AUTO_CONFIRM").lower() == "true"
        if "ARDAN_WORKSPACE" in os.environ:
            self.config.setdefault("agent", {})["workspace"] = os.getenv("ARDAN_WORKSPACE")

        # Env var override for ui
        if "ARDAN_SHOW_RAW_LLM_OUTPUT" in os.environ:
            self.config.setdefault("ui", {})["show_raw_llm_output"] = os.getenv("ARDAN_SHOW_RAW_LLM_OUTPUT").lower() == "true"
        if "ARDAN_THEME" in os.environ:
            self.config.setdefault("ui", {})["theme"] = os.getenv("ARDAN_THEME")

    def get(self, section: str, key: str, default: Any = None) -> Any:
        return self.config.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value: Any):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self._save_config()

    def _save_config(self):
        with open(self.config_path, "w") as f:
            yaml.safe_dump(self.config, f)

    @property
    def ollama_base_url(self) -> str:
        return self.get("ollama", "base_url", "http://localhost:11434")

    @property
    def ollama_model(self) -> str:
        return self.get("ollama", "model", "codellama:13b")

    @property
    def ollama_temperature(self) -> float:
        return self.get("ollama", "temperature", 0.2)

    @property
    def ollama_num_ctx(self) -> int:
        return self.get("ollama", "num_ctx", 8192)

    @property
    def ollama_stream(self) -> bool:
        return self.get("ollama", "stream", True)

    @property
    def agent_max_steps(self) -> int:
        return self.get("agent", "max_steps", 50)

    @property
    def agent_auto_confirm(self) -> bool:
        return self.get("agent", "auto_confirm", False)

    @property
    def agent_workspace(self) -> str:
        return self.get("agent", "workspace", "./ardan-output")

    @property
    def ui_show_raw_llm_output(self) -> bool:
        return self.get("ui", "show_raw_llm_output", False)

    @property
    def ui_theme(self) -> str:
        return self.get("ui", "theme", "dark")

settings = Settings()
