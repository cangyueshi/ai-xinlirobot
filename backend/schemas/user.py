from pydantic import BaseModel, Field
from models.user import UserRole


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    display_name: str = Field(min_length=1, max_length=100)
    role: UserRole = UserRole.VISITOR
    phone: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class WechatLogin(BaseModel):
    openid: str
    display_name: str = Field(min_length=1, max_length=100)
    role: UserRole = UserRole.VISITOR
    phone: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str | None = None
    openid: str | None = None
    display_name: str
    role: UserRole
    phone: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse