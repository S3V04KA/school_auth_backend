import datetime
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.user import get_user
from app.models.user import Role
from app.models import User as UserDBModel
from app.schemas.user import RoleInDB


async def change_role(db_session: AsyncSession, user_id: int, role_id: int) -> UserDBModel:
    user = await get_user(db_session, user_id)
    user.role_id = role_id
    user.updated_at = datetime.now()
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def get_all_roles(db_session: AsyncSession) -> list[Role]:
    return (await db_session.scalars(select(Role))).all()


async def get_role(db_session: AsyncSession, role_id: int) -> Role:
    return (await db_session.scalars(select(Role).options(selectinload(Role.users)).where(Role.id == role_id))).first()

async def create_role(db_session: AsyncSession, name: str) -> Role:
    new_role = Role(name=name)
    db_session.add(new_role)
    await db_session.commit()
    await db_session.refresh(new_role)
    
    role = await get_role(db_session, new_role.id)
    
    return new_role