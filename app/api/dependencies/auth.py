from fastapi import HTTPException
from app import models

from .user import CurrentUserDep


async def validate_is_authenticated(
    current_user: CurrentUserDep,
) -> models.User:
    """
    This just returns as the CurrentUserDep dependency already throws if there is an issue with the auth token.
    """
    return current_user


async def validate_is_admin(current_user: CurrentUserDep) -> models.User:
    if current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Not an admin")
    return current_user
