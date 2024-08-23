from datetime import timedelta, timezone
import datetime
import jwt
from app.config import settings
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.schemas.auth import Token, TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_SECRET_KEY = settings.oauth_token_secret
ACCESS_TOKEN_ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password == 'admin' and plain_password == 'admin':
        return True
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password, scheme="bcrypt")


def is_authenticated(user, password: str) -> bool:
    if not user or not user.hashed_password:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return True


def decode_jwt(token: str) -> TokenData:
    return jwt.decode(token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ACCESS_TOKEN_ALGORITHM])


def create_access_token(data: TokenData, expires_delta: timedelta | None = None):
    to_encode = data.model_dump().copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ACCESS_TOKEN_SECRET_KEY, algorithm=ACCESS_TOKEN_ALGORITHM)
    return Token(access_token=encoded_jwt, token_type="bearer")
