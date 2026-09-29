from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import UnauthorizedException, ValidationException
from app.db.models import User

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def register(self, email: str, password: str) -> tuple[User, str]:
        existing_user = await self.user_repository.get_by_email(email)

        if existing_user is not None:
            raise ValidationException(detail="Email already registered")

        hashed_password = hash_password(password)
        user = await self.user_repository.create(email=email, hashed_password=hashed_password)
        token = create_access_token(user.id)
        return user, token

    async def login(self, email: str, password: str) -> tuple[User, str]:
        user = await self.user_repository.get_by_email(email)

        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedException(detail="Invalid email or password")

        token = create_access_token(user.id)
        return user, token
