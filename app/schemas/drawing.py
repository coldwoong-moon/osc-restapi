from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class DrawingTreeCreate(BaseModel):
    name: str
    guid: str | None = None
    drawing_division: int | None = 0
    depth: int = 0
    parent_id: int | None = None


class DrawingTreeUpdate(BaseModel):
    name: str | None = None
    drawing_division: int | None = None


class DrawingTreeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    guid: str | None = None
    name: str
    drawing_division: int | None = Field(None, alias="drawing_div")
    depth: int
    parent_id: int | None = None
    project_id: int


class DrawingCreate(BaseModel):
    name: str
    revision: int
    create_date: datetime | None = None
    file_name: str | None = ""
    save_file_name: str | None = ""
    description: str | None = ""
    number: int | None = 0
    drawing_tree_id: int | None = None
    project_id: int


class DrawingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    revision: int
    create_date: datetime | None = None
    regist_date: datetime | None = None
    file_name: str | None = None
    save_file_name: str | None = None
    description: str | None = None
    number: int | None = None
    drawing_tree_id: int | None = None
    project_id: int


class ReferenceDrawingCreate(BaseModel):
    name: str
    elevation: float = 0
    file_name: str | None = ""
    save_file_name: str | None = ""


class ReferenceDrawingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str | None = None
    name: str
    elevation: float | None = None
    file_name: str | None = None
    save_file_name: str | None = None
    project_id: int
