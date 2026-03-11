from app.crud.base import CRUDBase
from app.models.part import PartInfo, PartAttribute, PartProductionRequest
from app.schemas.part import (
    PartInfoCreate,
    PartAttributeUpsert,
    PartProductionRequestCreate,
    PartProductionRequestResponse,
)


class CRUDPartInfo(CRUDBase[PartInfo, PartInfoCreate, PartInfoCreate]):
    pass


class CRUDPartAttribute(CRUDBase[PartAttribute, PartAttributeUpsert, PartAttributeUpsert]):
    pass


class CRUDPartProductionRequest(CRUDBase[PartProductionRequest, PartProductionRequestCreate, PartProductionRequestCreate]):
    pass


part_info = CRUDPartInfo(PartInfo)
part_attribute = CRUDPartAttribute(PartAttribute)
part_production_request = CRUDPartProductionRequest(PartProductionRequest)
