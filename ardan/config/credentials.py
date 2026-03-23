import os
import json
import base64
import uuid
from pathlib import Path
from typing import Dict, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


class CredentialsManager:
    def __init__(self):
        self.config_dir = Path.home() / ".ardan"
        self.config_dir.mkdir(exist_ok=True)
        self.credentials_file = self.config_dir / "credentials.json"
        self._key = self._get_machine_key()
        self._fernet = Fernet(self._key)
        self._credentials = self._load()

    def _get_machine_key(self) -> bytes:
        machine_id = str(uuid.getnode())
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"ardan-secure-salt-v1",
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))

    def _load(self) -> Dict[str, str]:
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, "r") as f:
                    data = json.load(f)
                    encrypted_blob = data.get("keys", "")
                    if encrypted_blob:
                        decrypted = self._fernet.decrypt(encrypted_blob.encode())
                        return json.loads(decrypted)
            except Exception:
                return {}
        return {}

    def _save(self):
        decrypted_json = json.dumps(self._credentials).encode()
        encrypted_blob = self._fernet.encrypt(decrypted_json).decode()
        with open(self.credentials_file, "w") as f:
            json.dump({"keys": encrypted_blob}, f)

    def set(self, provider: str, api_key: str):
        self._credentials[provider.lower()] = api_key
        self._save()

    def get(self, provider: str) -> Optional[str]:
        # Priority: Env Var -> Encrypted Store
        env_var = f"{provider.upper()}_API_KEY"
        if env_var in os.environ:
            return os.getenv(env_var)
        return self._credentials.get(provider.lower())

    def remove(self, provider: str):
        if provider.lower() in self._credentials:
            del self._credentials[provider.lower()]
            self._save()

    def list_masked(self) -> Dict[str, str]:
        return {
            p: f"{k[:4]}...{k[-4:]}" if len(k) > 8 else "***"
            for p, k in self._credentials.items()
        }


credentials_manager = CredentialsManager()
