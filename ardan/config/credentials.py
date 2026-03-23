import os
import json
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import uuid

class CredentialsManager:
    def __init__(self):
        self.config_dir = Path.home() / ".ardan"
        self.config_dir.mkdir(exist_ok=True)
        self.credentials_file = self.config_dir / "credentials.enc"
        self._key = self._get_machine_key()
        self._fernet = Fernet(self._key)
        self._credentials = self._load()

    def _get_machine_key(self) -> bytes:
        # Machine-derived key using MAC address or machine id
        machine_id = str(uuid.getnode())
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"ardan-salt-key-protection",
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))

    def _load(self) -> Dict[str, str]:
        if self.credentials_file.exists():
            try:
                encrypted_data = self.credentials_file.read_bytes()
                decrypted_data = self._fernet.decrypt(encrypted_data)
                return json.loads(decrypted_data)
            except:
                return {}
        return {}

    def _save(self):
        data = json.dumps(self._credentials).encode()
        encrypted_data = self._fernet.encrypt(data)
        self.credentials_file.write_bytes(encrypted_data)

    def set(self, provider: str, api_key: str):
        self._credentials[provider.lower()] = api_key
        self._save()

    def get(self, provider: str) -> Optional[str]:
        # Check environment variable first
        env_var_name = f"{provider.upper()}_API_KEY"
        if env_var_name in os.environ:
             return os.getenv(env_var_name)

        return self._credentials.get(provider.lower())

    def list(self) -> Dict[str, str]:
        # Return masked keys
        return {p: f"{k[:4]}...{k[-4:]}" if len(k) > 8 else "***" for p, k in self._credentials.items()}

    def remove(self, provider: str):
        if provider.lower() in self._credentials:
             del self._credentials[provider.lower()]
             self._save()
             return True
        return False

credentials_manager = CredentialsManager()
