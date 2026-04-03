import os
from pathlib import Path
from cryptography.fernet import Fernet

# Dynamic Path Resolution
SCRIPT_DIR = Path(__file__).parent.absolute()
KEY_FILE = SCRIPT_DIR / "vault.key"

class NikolaiVault:
    def __init__(self):
        self.key = self._load_key()
        self.cipher = Fernet(self.key)

    def _load_key(self):
        if not KEY_FILE.exists():
            print(f"[*] SEC: Generating new master key at {KEY_FILE}")
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as f:
                f.write(key)
            return key
        return open(KEY_FILE, "rb").read()

    def encrypt(self, plaintext: str) -> str:
        if not plaintext: return ""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        if not ciphertext: return ""
        try:
            return self.cipher.decrypt(ciphertext.encode()).decode()
        except:
            return "[DECRYPTION_FAILED]"

vault = NikolaiVault()
