from cryptography.fernet import Fernet
from django.conf import settings


def _fernet():
    return Fernet(settings.GITHUB_TOKEN_ENCRYPTION_KEY.encode())


def encrypt_token(raw_token: str) -> str:
    return _fernet().encrypt(raw_token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    return _fernet().decrypt(encrypted_token.encode()).decode()
