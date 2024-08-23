import datetime
from pydantic import BaseModel, ConfigDict


class Role(BaseModel):
    id: int
    name: str


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: str
    fullname: str


class AuthUserSchema(UserSchema):
    password: str


class LoginUserSchema(BaseModel):
    username: str
    password: str
    
class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str

class User(UserSchema):
    id: int


class UserResponse(User):
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UserResponseRules(UserResponse):
    role: Role


class UserPrivate(User):
    hashed_password: str


class RoleInDB(Role):
    users: list[UserResponse]

class ChangeRoleSchema(BaseModel):
    role_id: int
    user_id: int
    
class CreateRoleSchema(BaseModel):
    name: str