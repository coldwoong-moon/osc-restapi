from app.crud.base import CRUDBase
from app.models.location import ApartmentComplex, Floor, Zone
from app.schemas.location import (
    ApartmentComplexCreate,
    ApartmentComplexUpdate,
    FloorCreate,
    FloorUpdate,
    ZoneCreate,
    ZoneUpdate,
)


class CRUDApartmentComplex(CRUDBase[ApartmentComplex, ApartmentComplexCreate, ApartmentComplexUpdate]):
    pass


class CRUDFloor(CRUDBase[Floor, FloorCreate, FloorUpdate]):
    pass


class CRUDZone(CRUDBase[Zone, ZoneCreate, ZoneUpdate]):
    pass


apartment_complex = CRUDApartmentComplex(ApartmentComplex)
floor = CRUDFloor(Floor)
zone = CRUDZone(Zone)
