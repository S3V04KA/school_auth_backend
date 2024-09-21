from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.auth import RoleChecker
from app.api.dependencies.core import DBSessionDep
from app.crud.role import change_role, create_role, get_all_roles, get_role
from app.crud.user import get_user
from app.schemas.user import ChangeRoleSchema, CreateRoleSchema, Role, RoleInDB, UserResponseRules


router = APIRouter(
    prefix="/roles",
    tags=["roles"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def roles(db_session: DBSessionDep) -> list[Role]:
    return await get_all_roles(db_session)


@router.get("/id/{role_id}", dependencies=[Depends(RoleChecker("admin"))], description='Required admin access')
async def role(role_id: int, db_session: DBSessionDep) -> RoleInDB:
    return await get_role(db_session, role_id)


@router.put("/", dependencies=[Depends(RoleChecker("admin"))], description='Required admin access')
async def change_role_api(data: ChangeRoleSchema, db_session: DBSessionDep) -> UserResponseRules:
    role = await get_role(db_session, data.role_id)

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    user = await get_user(db_session, data.user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return await change_role(db_session, data.user_id, data.role_id)

@router.post("/", dependencies=[Depends(RoleChecker("admin"))], description='Required admin access')
async def create_role_api(data: CreateRoleSchema, db_session: DBSessionDep) -> RoleInDB:
    return await create_role(db_session, data.name)