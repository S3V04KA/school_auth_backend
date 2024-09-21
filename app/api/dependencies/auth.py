import logging
from typing import Annotated, Any
from fastapi import Depends, HTTPException
from app import models
from app.schemas.user import User

from .user import CurrentUserDep, get_current_user

class RoleChecker:
    def __init__(self, role: str) -> None:
        self.role = role
        
    def __call__(self, current_user: CurrentUserDep) -> bool:
        return current_user.role.name.lower() == self.role.lower()

async def validate_is_authenticated(
    current_user: CurrentUserDep,
) -> models.User:
    return current_user