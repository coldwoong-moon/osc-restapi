from app.crud.base import CRUDBase
from app.models.crane import StandardCrane, CraneItem, Crane
from app.schemas.crane import (
    StandardCraneCreate,
    StandardCraneUpdate,
    CraneItemCreate,
    CraneCreate,
    CraneUpdate,
)


class CRUDStandardCrane(CRUDBase[StandardCrane, StandardCraneCreate, StandardCraneUpdate]):
    pass


class CRUDCraneItem(CRUDBase[CraneItem, CraneItemCreate, CraneItemCreate]):
    pass


class CRUDCrane(CRUDBase[Crane, CraneCreate, CraneUpdate]):
    pass


standard_crane = CRUDStandardCrane(StandardCrane)
crane_item = CRUDCraneItem(CraneItem)
crane = CRUDCrane(Crane)
