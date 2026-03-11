from datetime import datetime
from pydantic import BaseModel, ConfigDict


class HouseholdsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str | None = None
    name: str
    aptcmpl_id: int | None = None
    project_id: int


class PartnerCreate(BaseModel):
    name: str
    guid: str
    business_number: str | None = ""


class PartnerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str | None = None
    name: str
    business_number: str | None = None


class MarkerCreate(BaseModel):
    name: str
    guid: str | None = None
    latitude: float
    longitude: float
    description: str | None = ""


class MarkerUpdate(BaseModel):
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    description: str | None = None


class MarkerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str | None = None
    name: str
    latitude: float
    longitude: float
    description: str | None = None
    project_id: int


class ProductionCompletedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str | None = None
    part_number: str
    completed_date: datetime | None = None
    project_id: int


class InstallCompletedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str | None = None
    part_number: str
    completed_date: datetime | None = None
    project_id: int


class CarryInRequestCreate(BaseModel):
    title: str
    guid: str | None = None
    status: int = 0
    request_date: datetime | None = None


class CarryInRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str | None = None
    title: str
    status: int
    request_date: datetime | None = None
    project_id: int


class ModelEnvironmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str | None = None
    name: str
    project_id: int


class ModelSceneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str | None = None
    name: str
    data: str | None = None
    project_id: int
