from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.roles import Role
from app.auth.tokens import decode_access_token, role_from_token_payload
from app.auth.users import DEMO_USERS
from app.core.config import Settings, get_settings

_bearer = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    username: str
    role: Role
    display_name: str
    organization: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    settings: Settings = Depends(get_settings),
) -> CurrentUser:
    if not settings.auth_enabled:
        return CurrentUser(
            username="dev-bypass",
            role=Role.ADMIN,
            display_name="Dev Bypass",
            organization="Local",
        )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(credentials.credentials, settings)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    username = str(payload.get("sub", ""))
    demo = DEMO_USERS.get(username)
    if demo is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    return CurrentUser(
        username=demo.username,
        role=role_from_token_payload(payload),
        display_name=demo.display_name,
        organization=demo.organization,
    )


def require_roles(*allowed: Role):
    def _checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed and user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role.value}' cannot perform this action",
            )
        return user

    return _checker
