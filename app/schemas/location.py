from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ApartmentComplexCreate(BaseModel):
    name: str
    guid: str


class ApartmentComplexUpdate(BaseModel):
    name: str | None = None


class ApartmentComplexResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str | None = None
    name: str
    project_id: int


class FloorCreate(BaseModel):
    name: str
    aptcmpl_id: int


class FloorUpdate(BaseModel):
    name: str | None = None


class FloorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str | None = None
    name: str
    aptcmpl_id: int
    project_id: int


class ZoneCreate(BaseModel):
    name: str
    guid: str | None = None
    end_date: datetime | None = None
    color: str | None = None
    points: str | None = None


class ZoneUpdate(BaseModel):
    name: str | None = None
    end_date: datetime | None = None
    color: str | None = None
    points: str | None = None


class ZoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    guid: str | None = None
    name: str
    end_date: datetime | None = None
    color: str | None = None
    points: str | None = Field(None, alias="polygon_point")
    project_id: int
    renewal_time: datetime | None = None
