from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException
from app.repositories.user_repository import UserRepository
from app.db.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise UnauthorizedException()

    user = await UserRepository(session).get_by_id(user_id)

    if user is None:
        raise UnauthorizedException()

    return user
