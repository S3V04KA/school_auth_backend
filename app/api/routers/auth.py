from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.core import DBSessionDep
from app.crud.user import create_user, get_user_by_email, get_user_by_username
from app.schemas.auth import Token, TokenData
from app.schemas.user import AuthUserSchema, LoginUserSchema, UserResponse
from app.utils.auth import create_access_token, verify_password


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post("/login", response_model=Token)
async def login(data: LoginUserSchema, db_session: DBSessionDep) -> Token:
    user = await get_user_by_email(db_session, data.username)
    if user:
        if verify_password(data.password, user.hashed_password):
            return create_access_token(TokenData(username=user.username, email=user.email))
        else:
            raise HTTPException(status_code=400, detail="Incorrect password")

    user = await get_user_by_username(db_session, data.username)
    if user:
        if verify_password(data.password, user.hashed_password):
            return create_access_token(TokenData(username=user.username, email=user.email))
        else:
            raise HTTPException(status_code=400, detail="Incorrect password")

    raise HTTPException(status_code=400, detail="Incorrect username or password")


@router.post("/token", include_in_schema=False)
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db_session: DBSessionDep) -> Token:
    return await login(form_data, db_session)


@router.post("/register")
async def register(user: AuthUserSchema, db_session: DBSessionDep) -> UserResponse:
    tuser = await get_user_by_email(db_session, user.email)

    if tuser:
        raise HTTPException(status_code=400, detail="Email already registered")

    tuser = await get_user_by_username(db_session, user.username)

    if tuser:
        raise HTTPException(status_code=400, detail="Username already registered")

    user = await create_user(db_session, user)
    return user
