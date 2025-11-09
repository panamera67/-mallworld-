import datetime
import os

import jwt


def generate_admin_token():
    """Generate secure JWT token for admin access."""
    secret_key = os.getenv("JWT_SECRET_KEY", "lia_ultra_secure_jwt_secret_2024_$%^&*()_+")

    payload = {
        "sub": "lia-admin",
        "role": "admin",
        "permissions": ["read", "write", "admin"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=365),
        "iat": datetime.datetime.utcnow(),
        "iss": "lia-ultimate-ai",
    }

    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


if __name__ == "__main__":
    admin_token = generate_admin_token()
    print(f"🔐 ADMIN_JWT_TOKEN={admin_token}")
    print("✅ Copy this token to your .env file as ADMIN_JWT_TOKEN")
