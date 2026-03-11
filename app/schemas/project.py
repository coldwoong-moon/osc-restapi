from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    guid: str
    cnstrct_begin_date: datetime | None = None
    cnstrct_end_date: datetime | None = None
    manager_id: int


class ProjectUpdate(BaseModel):
    name: str | None = None
    cnstrct_begin_date: datetime | None = None
    cnstrct_end_date: datetime | None = None
    first_cnstrct_date: datetime | None = None
    manager_id: int | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str
    name: str
    cnstrct_begin_date: datetime | None = None
    cnstrct_end_date: datetime | None = None
    first_cnstrct_date: datetime | None = None
    manager_id: int
    renewal_time: datetime | None = None


class ProjectModelCreate(BaseModel):
    name: str
    guid: str
    description: str | None = ""
    project_id: int


class ProjectModelUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str | None = None
    name: str
    description: str | None = None
    project_id: int
    revision: int | None = None
    renewal_time: datetime | None = None


class ProjectUserCreate(BaseModel):
    user_id: int
    role_id: int


class ProjectUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: int
    user_id: int
    role_id: int
