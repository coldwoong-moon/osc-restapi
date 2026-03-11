from app.crud.base import CRUDBase
from app.models.misc import Partner, Marker, ModelEnvironment, ModelScene
from app.models.carry_in import CarryInRequest
from app.schemas.misc import (
    PartnerCreate,
    MarkerCreate,
    MarkerUpdate,
    CarryInRequestCreate,
)


class CRUDPartner(CRUDBase[Partner, PartnerCreate, PartnerCreate]):
    pass


class CRUDMarker(CRUDBase[Marker, MarkerCreate, MarkerUpdate]):
    pass


class CRUDCarryInRequest(CRUDBase[CarryInRequest, CarryInRequestCreate, CarryInRequestCreate]):
    pass


partner = CRUDPartner(Partner)
marker = CRUDMarker(Marker)
carry_in_request = CRUDCarryInRequest(CarryInRequest)
