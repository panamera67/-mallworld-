import os
from datetime import datetime, timedelta
from typing import Dict

from cryptography.fernet import Fernet
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class SecurityManager:
    def __init__(self):
        self.encryption_key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
        self.cipher_suite = Fernet(self.encryption_key)
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "default-secret-change-in-production")
        self.algorithm = "HS256"

    def encrypt_data(self, data: str) -> str:
        return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

    def create_jwt(self, payload: dict, expires_hours: int = 24) -> str:
        payload.update(
            {
                "exp": datetime.utcnow() + timedelta(hours=expires_hours),
                "iat": datetime.utcnow(),
                "iss": "lia-ultimate-ai",
            }
        )
        return jwt.encode(payload, self.jwt_secret, algorithm=self.algorithm)

    def verify_jwt(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.jwt_secret, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expiré"
            ) from exc
        except jwt.InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide"
            ) from exc


security = HTTPBearer()
security_manager = SecurityManager()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict:
    return security_manager.verify_jwt(credentials.credentials)
