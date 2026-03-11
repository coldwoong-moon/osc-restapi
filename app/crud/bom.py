from app.crud.base import CRUDBase
from app.models.bom import BillOfMaterial, PartQuantity, PartMaterial
from app.schemas.bom import BOMCreate, PartQuantityCreate


class CRUDBillOfMaterial(CRUDBase[BillOfMaterial, BOMCreate, BOMCreate]):
    pass


class CRUDPartQuantity(CRUDBase[PartQuantity, PartQuantityCreate, PartQuantityCreate]):
    pass


bom = CRUDBillOfMaterial(BillOfMaterial)
part_quantity = CRUDPartQuantity(PartQuantity)
