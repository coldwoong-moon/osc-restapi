from pydantic import BaseModel, ConfigDict, Field


class StandardCraneCreate(BaseModel):
    name: str
    guid: str
    color: str | None = ""


class StandardCraneUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


class StandardCraneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str | None = None
    name: str
    color: str | None = None
    project_id: int


class CraneItemCreate(BaseModel):
    guid: str
    weight: float
    radius: float
    standard_crane_id: int


class CraneItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str | None = None
    weight: float
    radius: float
    standard_crane_id: int


class CraneCreate(BaseModel):
    guid: str
    description: str | None = ""
    activation: bool = True
    geo_point: str | None = ""
    standard_crane_id: int


class CraneUpdate(BaseModel):
    description: str | None = None
    activation: bool | None = None
    geo_point: str | None = None


class CraneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    guid: str | None = None
    description: str | None = None
    activation: bool
    geo_point: str | None = Field(None, alias="geometry_point")
    standard_crane_id: int
