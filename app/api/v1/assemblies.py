from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.crud.assembly import assembly_info as crud_assembly
from app.db.session import get_db
from app.models.assembly import AssemblyInfo
from app.schemas.assembly import AssemblyInfoCreate, AssemblyInfoResponse, AssemblyMappingUpdate

router = APIRouter(tags=["Assemblies"])


@router.get("/projects/{project_id}/assemblies", response_model=list[AssemblyInfoResponse], summary="어셈블리 목록 조회")
def list_assemblies(project_id: int, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_assembly.get_multi(db, skip=skip, limit=limit, filters={"project_id": project_id})
    return results


@router.post("/projects/{project_id}/assemblies", response_model=list[AssemblyInfoResponse], status_code=status.HTTP_201_CREATED, summary="어셈블리 일괄 생성")
def create_assemblies(project_id: int, assemblies_in: list[AssemblyInfoCreate], response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    for item in assemblies_in:
        item.project_id = project_id
    objs = crud_assembly.create_multi(db, objs_in=assemblies_in)
    response.headers["Location"] = f"/api/v1/projects/{project_id}/assemblies"
    return objs


@router.delete("/projects/{project_id}/assemblies", status_code=status.HTTP_204_NO_CONTENT, summary="프로젝트 어셈블리 전체 삭제")
def delete_assemblies(project_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    db.execute(delete(AssemblyInfo).where(AssemblyInfo.project_id == project_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/assemblies/{assembly_guid}/mapping", response_model=AssemblyInfoResponse, summary="어셈블리 매핑 수정")
def update_assembly_mapping(assembly_guid: str, mapping_in: AssemblyMappingUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = db.scalar(select(AssemblyInfo).where(AssemblyInfo.guid == assembly_guid))
    if not obj:
        raise NotFoundException("AssemblyInfo", assembly_guid)
    update_data = mapping_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj
