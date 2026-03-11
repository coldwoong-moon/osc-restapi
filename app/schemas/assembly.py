from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AssemblyInfoCreate(BaseModel):
    guid: str
    assembly_number: str | None = ""
    classify: int | None = 0
    classify_name: str | None = ""
    width: float | None = 0
    height: float | None = 0
    length: float | None = 0
    volume: float | None = 0
    weight: float | None = 0
    project_id: int
    revision: int | None = 0
    number: int | None = 0
    project_model_id: int | None = None
    structure_id: int | None = None


class AssemblyInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    guid: str
    assembly_number: str | None = None
    classify: int | None = None
    classify_name: str | None = None
    width: float | None = None
    height: float | None = None
    length: float | None = None
    volume: float | None = None
    weight: float | None = None
    project_id: int
    revision: int | None = None
    number: int | None = None
    project_model_id: int | None = None
    structure_id: int | None = None
    floor_id: int | None = None
    zone_id: int | None = None
    updated_at: datetime | None = None


class AssemblyMappingUpdate(BaseModel):
    floor_id: int | None = None
    zone_id: int | None = None
    structure_id: int | None = None
