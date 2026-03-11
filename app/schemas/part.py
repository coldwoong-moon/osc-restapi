from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PartInfoCreate(BaseModel):
    guid: str
    aptcmpl_id: int | None = None
    floor_id: int | None = None
    zone_id: int | None = None
    project_id: int


class PartInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guid: str
    aptcmpl_id: int | None = None
    floor_id: int | None = None
    zone_id: int | None = None
    project_id: int
    renewal_time: datetime | None = None


class PartAttributeUpsert(BaseModel):
    part_number: str
    volume: float | None = 0
    ton: float | None = 0
    project_id: int


class PartAttributeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    part_number: str
    volume: float | None = None
    ton: float | None = None
    project_id: int


class PartProductionRequestCreate(BaseModel):
    part_number: str
    input_count: int
    install_prearnge_date: str
    prdctn_posbl_date: str
    confirm_status: int = 0
    project_id: int


class PartProductionRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    part_number: str
    input_count: int
    install_prearnge_date: str
    prdctn_posbl_date: str
    confirm_status: int
    project_id: int
