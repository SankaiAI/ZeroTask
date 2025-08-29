import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.config import settings

class TokenEncryption:
    """Secure token encryption utility - PRD Section 7.5 Data Governance"""
    
    def __init__(self):
        self.key = self._derive_key()
        self.fernet = Fernet(self.key)
    
    def _derive_key(self) -> bytes:
        """Derive encryption key from machine-specific data + app secret"""
        # Use machine ID and app secret from settings
        machine_id = settings.machine_id
        app_secret = settings.app_secret
        
        password = f"{machine_id}:{app_secret}".encode()
        salt = b'zerotask-salt-v1'  # Static salt for consistent key derivation
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Strong iteration count
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt API token for secure storage"""
        if not token:
            raise ValueError("Token cannot be empty")
        return self.fernet.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt stored token for API calls"""
        if not encrypted_token:
            raise ValueError("Encrypted token cannot be empty")
        return self.fernet.decrypt(encrypted_token.encode()).decode()

# Global encryption instance
token_encryption = TokenEncryption()