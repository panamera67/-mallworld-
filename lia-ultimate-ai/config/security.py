import os
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
import jwt


class SecurityManager:
    def __init__(self):
        self.encryption_key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
        self.cipher_suite = Fernet(self.encryption_key)
        self.jwt_secret = os.getenv("JWT_SECRET", "default-secret-change-in-production")

    def encrypt_data(self, data: str) -> str:
        """Chiffrement AES-256 des données sensibles."""
        return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Déchiffrement des données."""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

    def create_jwt(self, payload: dict, expires_hours: int = 24) -> str:
        """Création de JWT sécurisé."""
        payload.update(
            {
                "exp": datetime.utcnow() + timedelta(hours=expires_hours),
                "iat": datetime.utcnow(),
                "iss": "lia-ultimate-ai",
            }
        )
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def verify_jwt(self, token: str) -> dict:
        """Vérification de JWT."""
        try:
            return jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError as exc:
            raise Exception("Token expiré") from exc
        except jwt.InvalidTokenError as exc:
            raise Exception("Token invalide") from exc


security = SecurityManager()
