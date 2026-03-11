from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    guid: str | None = None
    email: str
    name: str
    partner_id: int | None = None
    department: str | None = Field(None, alias="dept")
    rank: str | None = None
    tel: str | None = Field(None, alias="telno")
    mobile: str | None = Field(None, alias="mbtlnum")
    is_enabled: bool = Field(False, alias="isEnabled")
    authorities: list[str] = []


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: LoginResponse


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
