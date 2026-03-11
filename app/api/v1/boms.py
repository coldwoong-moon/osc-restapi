from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.crud.bom import bom as crud_bom
from app.db.session import get_db
from app.models.bom import BillOfMaterial, PartMaterial, PartQuantity
from app.schemas.bom import BOMCreate, BOMResponse, PartMaterialResponse, PartQuantityCreate, PartQuantityResponse

router = APIRouter(tags=["BOMs"])


@router.get("/projects/{project_id}/boms", response_model=list[BOMResponse], summary="BOM 목록 조회")
def list_boms(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_bom.get_multi(db, skip=skip, limit=limit, filters={"project_id": project_id})
    return results


@router.post("/projects/{project_id}/boms", response_model=BOMResponse, status_code=status.HTTP_201_CREATED, summary="BOM 생성")
def create_bom(project_id: int, bom_in: BOMCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    bom_in.project_id = project_id
    obj = crud_bom.create(db, obj_in=bom_in)
    response.headers["Location"] = f"/api/v1/projects/{project_id}/boms/{obj.id}"
    return obj


@router.get("/projects/{project_id}/part-materials", response_model=list[PartMaterialResponse], summary="파트 자재 목록 조회")
def list_part_materials(project_id: int, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results = db.scalars(
        select(PartMaterial).where(PartMaterial.project_id == project_id).offset(skip).limit(limit)
    ).all()
    return results


@router.get("/projects/{project_id}/part-quantities", response_model=list[PartQuantityResponse], summary="파트 수량 목록 조회")
def list_part_quantities(project_id: int, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results = db.scalars(
        select(PartQuantity).where(PartQuantity.project_id == project_id).offset(skip).limit(limit)
    ).all()
    return results
