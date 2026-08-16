from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from config import settings

password_hash = PasswordHash.recommended()


def hash_password(senha: str) -> str:
    return password_hash.hash(senha)


def verify_password(senha: str, senha_hash: str) -> bool:
    return password_hash.verify(senha, senha_hash)


def create_access_token(subject: str, perfil: str) -> str:
    expira_em = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "perfil": perfil, "exp": expira_em}
    return jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=[settings.algorithm])