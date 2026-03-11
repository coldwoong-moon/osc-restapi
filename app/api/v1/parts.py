from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.crud.part import part_attribute as crud_part_attribute
from app.crud.part import part_info as crud_part_info
from app.crud.part import part_production_request as crud_ppr
from app.db.session import get_db
from app.models.part import PartAttribute, PartInfo, PartProductionRequest
from app.schemas.part import (
    PartAttributeResponse,
    PartAttributeUpsert,
    PartInfoCreate,
    PartInfoResponse,
    PartProductionRequestCreate,
    PartProductionRequestResponse,
)

router = APIRouter(tags=["Parts"])


@router.get("/projects/{project_id}/parts", response_model=list[PartInfoResponse], summary="파트 목록 조회")
def list_parts(project_id: int, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_part_info.get_multi(db, skip=skip, limit=limit, filters={"project_id": project_id})
    return results


@router.post("/projects/{project_id}/parts", response_model=PartInfoResponse, status_code=status.HTTP_201_CREATED, summary="파트 생성/업서트")
def upsert_part(project_id: int, part_in: PartInfoCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    existing = db.scalar(select(PartInfo).where(PartInfo.guid == part_in.guid))
    if existing:
        update_data = part_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing
    part_in.project_id = project_id
    obj = crud_part_info.create(db, obj_in=part_in)
    response.headers["Location"] = f"/api/v1/projects/{project_id}/parts/{obj.id}"
    return obj


@router.delete("/parts/{part_id}", status_code=status.HTTP_204_NO_CONTENT, summary="파트 삭제")
def delete_part(part_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_part_info.get(db, part_id)
    if not obj:
        raise NotFoundException("PartInfo", part_id)
    db.delete(obj)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/projects/{project_id}/part-attributes", response_model=list[PartAttributeResponse], summary="파트 속성 목록 조회")
def list_part_attributes(project_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results = db.scalars(select(PartAttribute).where(PartAttribute.project_id == project_id)).all()
    return results


@router.put("/projects/{project_id}/part-attributes", response_model=list[PartAttributeResponse], summary="파트 속성 업서트")
def upsert_part_attributes(project_id: int, attrs_in: list[PartAttributeUpsert], db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results = []
    for attr in attrs_in:
        existing = db.scalar(
            select(PartAttribute).where(
                PartAttribute.part_number == attr.part_number,
                PartAttribute.project_id == project_id,
            )
        )
        if existing:
            existing.volume = attr.volume
            existing.ton = attr.ton
            results.append(existing)
        else:
            obj = PartAttribute(part_number=attr.part_number, volume=attr.volume, ton=attr.ton, project_id=project_id)
            db.add(obj)
            results.append(obj)
    db.commit()
    for obj in results:
        db.refresh(obj)
    return results


@router.get("/projects/{project_id}/part-production-requests", response_model=list[PartProductionRequestResponse], summary="파트 생산 요청 목록 조회")
def list_part_production_requests(project_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results = db.scalars(select(PartProductionRequest).where(PartProductionRequest.project_id == project_id)).all()
    return results


@router.post("/projects/{project_id}/part-production-requests", response_model=PartProductionRequestResponse, status_code=status.HTTP_201_CREATED, summary="파트 생산 요청 생성")
def create_part_production_request(project_id: int, ppr_in: PartProductionRequestCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    ppr_in.project_id = project_id
    obj = crud_ppr.create(db, obj_in=ppr_in)
    response.headers["Location"] = f"/api/v1/projects/{project_id}/part-production-requests/{obj.part_number}"
    return obj
