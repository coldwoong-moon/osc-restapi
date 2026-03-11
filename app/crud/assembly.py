from app.crud.base import CRUDBase
from app.models.assembly import AssemblyInfo
from app.schemas.assembly import AssemblyInfoCreate, AssemblyMappingUpdate


class CRUDAssemblyInfo(CRUDBase[AssemblyInfo, AssemblyInfoCreate, AssemblyMappingUpdate]):
    pass


assembly_info = CRUDAssemblyInfo(AssemblyInfo)
