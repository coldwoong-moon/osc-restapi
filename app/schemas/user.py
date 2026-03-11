from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    guid: str
    partner_id: int | None = None
    department: str | None = ""
    rank: str | None = ""
    tel: str | None = ""
    mobile: str | None = ""


class UserUpdate(BaseModel):
    name: str | None = None
    partner_id: int | None = None
    department: str | None = None
    rank: str | None = None
    tel: str | None = None
    mobile: str | None = None


class UserResponse(BaseModel):
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
    is_enabled: bool = Field(..., alias="isEnabled")


class PasswordUpdate(BaseModel):
    password: str
    new_password: str


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
