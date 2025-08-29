from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.tokens import Token
from app.utils.encryption import token_encryption

class AuthService:
    """Authentication service for managing encrypted tokens - PRD Section 8 Architecture"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def store_token(self, provider: str, token: str) -> bool:
        """Securely store encrypted token for a provider"""
        try:
            # Encrypt the token
            encrypted_token = token_encryption.encrypt_token(token)
            
            # Check if token already exists for this provider
            existing = self.db.query(Token).filter(Token.provider == provider).first()
            
            if existing:
                # Update existing token
                existing.encrypted_token = encrypted_token
                existing.updated_at = datetime.utcnow()
            else:
                # Create new token record
                new_token = Token(
                    provider=provider,
                    encrypted_token=encrypted_token
                )
                self.db.add(new_token)
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to store token for {provider}: {str(e)}")
    
    def get_decrypted_token(self, provider: str) -> str:
        """Retrieve and decrypt token for API calls"""
        token_record = self.db.query(Token).filter(Token.provider == provider).first()
        
        if not token_record:
            raise ValueError(f"No token found for provider: {provider}")
        
        try:
            return token_encryption.decrypt_token(token_record.encrypted_token)
        except Exception as e:
            raise ValueError(f"Failed to decrypt token for {provider}: {str(e)}")
    
    def has_token(self, provider: str) -> bool:
        """Check if we have a stored token for a provider"""
        return self.db.query(Token).filter(Token.provider == provider).first() is not None
    
    async def remove_token(self, provider: str) -> bool:
        """Remove stored token for a provider"""
        try:
            token_record = self.db.query(Token).filter(Token.provider == provider).first()
            
            if token_record:
                self.db.delete(token_record)
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to remove token for {provider}: {str(e)}")
    
    def list_connected_providers(self) -> list:
        """Get list of providers with stored tokens"""
        tokens = self.db.query(Token).all()
        return [token.provider for token in tokens]