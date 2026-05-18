from pydantic import BaseModel, Field
from models.user import UserRole, AccountStatus


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    display_name: str = Field(min_length=1, max_length=100)
    role: UserRole = UserRole.VISITOR
    email: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class AdminLogin(BaseModel):
    username: str
    password: str


class WechatLogin(BaseModel):
    openid: str
    display_name: str = Field(min_length=1, max_length=100)
    avatar_url: str | None = None


class MpLoginRequest(BaseModel):
    """微信小程序 wx.login() → code → jscode2session"""
    code: str


class ChangePassword(BaseModel):
    old_password: str | None = None
    new_password: str = Field(min_length=6, max_length=128)


class ForceChangePassword(BaseModel):
    new_password: str = Field(min_length=6, max_length=128)


class ForgotPassword(BaseModel):
    email: str


class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=6, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str | None = None
    openid: str | None = None
    display_name: str
    role: UserRole
    email: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    specialties: str | None = None
    status: AccountStatus
    must_change_password: bool = False
    sub_admin_permissions: str | None = None
    created_at: str | None = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class CreateCounselor(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    email: str | None = None
    bio: str | None = None
    specialties: str | None = None


class UpdateCounselor(BaseModel):
    display_name: str | None = None
    email: str | None = None
    bio: str | None = None
    specialties: str | None = None


class CreateSubAdmin(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    email: str | None = None
    permissions: str | None = None


class UpdateSubAdmin(BaseModel):
    display_name: str | None = None
    email: str | None = None
    permissions: str | None = None


class ResetUserPassword(BaseModel):
    new_password: str = Field(min_length=6, max_length=128)