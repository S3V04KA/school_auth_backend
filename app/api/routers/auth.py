from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import delete, select

from app.api.dependencies.auth import RoleChecker, validate_is_authenticated
from app.api.dependencies.core import DBSessionDep
from app.api.dependencies.user import get_current_user
from app.crud.user import create_user, get_user_by_email, get_user_by_username
from app.models.user import Session
from app.schemas.auth import Token, TokenData
from app.schemas.user import AuthUserSchema, LoginUserSchema, User, UserResponse
from app.utils.auth import create_access_token, get_session, verify_password


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
            return await create_access_token(TokenData(username=user.username, email=user.email, id=user.id), db_session)
        else:
            raise HTTPException(status_code=400, detail="Incorrect password")

    user = await get_user_by_username(db_session, data.username)
    if user:
        if verify_password(data.password, user.hashed_password):
            return await create_access_token(TokenData(username=user.username, email=user.email, id=user.id), db_session)
        else:
            raise HTTPException(status_code=400, detail="Incorrect password")

    raise HTTPException(status_code=400, detail="Incorrect username or password")


@router.post('/logout', dependencies=[Depends(validate_is_authenticated)])
async def logout(user: Annotated[User, Depends(get_current_user)], req: Request, db_session: DBSessionDep):
    response = Response(status_code=200, headers={"Content-Type": "application/json", "Access-Control-Allow-Credentials": "true"})
    response.delete_cookie(key="token")
    response.delete_cookie(key="token_type")

    await db_session.execute(delete(Session).where(Session.user_id == user.id, Session.token == req.cookies["token"]))
    await db_session.commit()

    return response


@router.post("/token", include_in_schema=False)
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db_session: DBSessionDep) -> Token:
    return await login(form_data, db_session)


@router.post("/register", dependencies=[Depends(RoleChecker("admin"))], description='Required admin access')
async def register(user: AuthUserSchema, db_session: DBSessionDep) -> UserResponse:
    tuser = await get_user_by_email(db_session, user.email)

    if tuser:
        raise HTTPException(status_code=400, detail="Email already registered")

    tuser = await get_user_by_username(db_session, user.username)

    if tuser:
        raise HTTPException(status_code=400, detail="Username already registered")

    user = await create_user(db_session, user)
    return user
