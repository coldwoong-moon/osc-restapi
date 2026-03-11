from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BOMCreate(BaseModel):
    name: str
    guid: str
    revision: int
    create_date: datetime | None = None
    file_name: str | None = ""
    save_file_name: str | None = ""
    description: str | None = ""
    number: int | None = 0
    project_id: int
    project_model_id: int


class BOMResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str | None = None
    name: str
    revision: int
    create_date: datetime | None = None
    regist_date: datetime | None = None
    file_name: str | None = None
    save_file_name: str | None = None
    description: str | None = None
    number: int | None = None
    project_id: int
    project_model_id: int


class PartQuantityCreate(BaseModel):
    project_model_id: int
    bom_id: int
    project_id: int
    description: str | None = ""


class PartQuantityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_model_id: int
    bom_id: int
    project_id: int
    description: str | None = None


class PartMaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    part_number: str
    prefix: str | None = None
    qty: int | None = None
    hold_qty: int | None = None
    available_qty: int | None = None
    volume: float | None = None
    sum_volume: float | None = None
    strength: str | None = None
    width: float | None = None
    height: float | None = None
    length: float | None = None
    project_model_id: int | None = None
    project_id: int
