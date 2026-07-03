from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.deps import CurrentUser, get_current_user
from app.auth.tokens import create_access_token
from app.auth.users import authenticate
from app.core.config import Settings, get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginInput(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=4, max_length=100)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    display_name: str
    organization: str


class MeResponse(BaseModel):
    username: str
    role: str
    display_name: str
    organization: str


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginInput, settings: Settings = Depends(get_settings)) -> LoginResponse:
    user = authenticate(payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user, settings)
    return LoginResponse(
        access_token=token,
        username=user.username,
        role=user.role.value,
        display_name=user.display_name,
        organization=user.organization,
    )


@router.get("/me", response_model=MeResponse)
def me(user: CurrentUser = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        username=user.username,
        role=user.role.value,
        display_name=user.display_name,
        organization=user.organization,
    )
