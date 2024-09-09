from app.models import User as UserDBModel
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import AuthUserSchema, ChangePasswordSchema
from app.utils.auth import get_password_hash, verify_password


async def get_user(db_session: AsyncSession, user_id: int) -> UserDBModel:
    user = (
        await db_session.scalars(
            select(UserDBModel).options(selectinload(UserDBModel.role)).where(UserDBModel.id == user_id)
        )
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_user_by_email(db_session: AsyncSession, email: str) -> UserDBModel:
    user = (
        await db_session.scalars(
            select(UserDBModel).options(selectinload(UserDBModel.role)).where(UserDBModel.email == email)
        )
    ).first()
    return user


async def get_user_by_username(db_session: AsyncSession, username: str) -> UserDBModel:
    return (await db_session.scalars(select(UserDBModel).where(UserDBModel.username == username))).first()


async def get_users(db_session: AsyncSession) -> list[UserDBModel]:
    return (await db_session.scalars(select(UserDBModel).options(selectinload(UserDBModel.role)))).all()


async def create_user(db_session: AsyncSession, user: AuthUserSchema) -> UserDBModel:
    password = get_password_hash(user.password)
    del user.password
    new_user = UserDBModel(**user.model_dump(), hashed_password=password, role_id=2)
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)
    return new_user

async def change_password(db_session: AsyncSession, data: ChangePasswordSchema, user: UserDBModel) -> UserDBModel:
    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    chuser = (await db_session.scalars(select(UserDBModel).where(UserDBModel.id == user.id))).first()
    chuser.hashed_password = get_password_hash(data.new_password)
    await db_session.commit()
    await db_session.refresh(chuser)
    return chuser