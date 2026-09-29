from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserResponse, Token
from app.api.dependencies import get_current_user
from app.db.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(payload: UserCreate, session: AsyncSession = Depends(get_session)):
    auth_service = AuthService(session)
    user, _ = await auth_service.register(payload.email, payload.password)
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    auth_service = AuthService(session)
    _, token = await auth_service.login(form_data.username, form_data.password)
    return Token(access_token=token)

@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
