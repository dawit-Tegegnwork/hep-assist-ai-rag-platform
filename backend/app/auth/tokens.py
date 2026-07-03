from datetime import UTC, datetime, timedelta

import jwt

from app.auth.roles import Role
from app.auth.users import DemoUser
from app.core.config import Settings


def create_access_token(user: DemoUser, settings: Settings) -> str:
    expires = datetime.now(UTC) + timedelta(hours=settings.auth_token_expire_hours)
    payload = {
        "sub": user.username,
        "role": user.role.value,
        "display_name": user.display_name,
        "organization": user.organization,
        "exp": expires,
    }
    return jwt.encode(payload, settings.auth_secret_key, algorithm=settings.auth_algorithm)


def decode_access_token(token: str, settings: Settings) -> dict[str, object]:
    return jwt.decode(token, settings.auth_secret_key, algorithms=[settings.auth_algorithm])


def role_from_token_payload(payload: dict[str, object]) -> Role:
    return Role(str(payload["role"]))
