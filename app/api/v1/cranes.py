from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.crud.crane import crane as crud_crane
from app.crud.crane import crane_item as crud_crane_item
from app.crud.crane import standard_crane as crud_standard_crane
from app.db.session import get_db
from app.models.crane import Crane, CraneItem, StandardCrane
from app.schemas.crane import (
    CraneCreate,
    CraneItemCreate,
    CraneItemResponse,
    CraneResponse,
    CraneUpdate,
    StandardCraneCreate,
    StandardCraneResponse,
    StandardCraneUpdate,
)

router = APIRouter(tags=["Cranes"])


@router.get("/projects/{project_id}/cranes/standards", response_model=list[StandardCraneResponse], summary="표준 크레인 목록 조회")
def list_standard_cranes(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_standard_crane.get_multi(db, skip=skip, limit=limit, filters={"project_id": project_id})
    return results


@router.post("/projects/{project_id}/cranes/standards", response_model=StandardCraneResponse, status_code=status.HTTP_201_CREATED, summary="표준 크레인 생성")
def create_standard_crane(project_id: int, crane_in: StandardCraneCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = StandardCrane(name=crane_in.name, guid=crane_in.guid, color=crane_in.color, project_id=project_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    response.headers["Location"] = f"/api/v1/projects/{project_id}/cranes/standards/{obj.id}"
    return obj


@router.put("/cranes/standards/{crane_id}", response_model=StandardCraneResponse, summary="표준 크레인 수정")
def update_standard_crane(crane_id: int, crane_in: StandardCraneUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_standard_crane.get(db, crane_id)
    if not obj:
        raise NotFoundException("StandardCrane", crane_id)
    return crud_standard_crane.update(db, db_obj=obj, obj_in=crane_in)


@router.delete("/cranes/standards/{crane_id}", status_code=status.HTTP_204_NO_CONTENT, summary="표준 크레인 삭제")
def delete_standard_crane(crane_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_standard_crane.get(db, crane_id)
    if not obj:
        raise NotFoundException("StandardCrane", crane_id)
    db.delete(obj)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/projects/{project_id}/cranes", response_model=list[CraneResponse], summary="크레인 목록 조회")
def list_cranes(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results = db.scalars(
        select(Crane)
        .join(StandardCrane, Crane.standard_crane_id == StandardCrane.id)
        .where(StandardCrane.project_id == project_id)
        .offset(skip)
        .limit(limit)
    ).all()
    return results


@router.post("/projects/{project_id}/cranes", response_model=CraneResponse, status_code=status.HTTP_201_CREATED, summary="크레인 생성")
def create_crane(project_id: int, crane_in: CraneCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = Crane(
        guid=crane_in.guid,
        description=crane_in.description,
        activation=crane_in.activation,
        geometry_point=crane_in.geo_point,
        standard_crane_id=crane_in.standard_crane_id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    response.headers["Location"] = f"/api/v1/cranes/{obj.id}"
    return obj


@router.put("/cranes/{crane_id}", response_model=CraneResponse, summary="크레인 수정")
def update_crane(crane_id: int, crane_in: CraneUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_crane.get(db, crane_id)
    if not obj:
        raise NotFoundException("Crane", crane_id)
    update_data = crane_in.model_dump(exclude_unset=True)
    if "geo_point" in update_data:
        update_data["geometry_point"] = update_data.pop("geo_point")
    for field, value in update_data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cranes/{crane_id}", status_code=status.HTTP_204_NO_CONTENT, summary="크레인 삭제")
def delete_crane(crane_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_crane.get(db, crane_id)
    if not obj:
        raise NotFoundException("Crane", crane_id)
    db.delete(obj)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/projects/{project_id}/cranes/items", response_model=list[CraneItemResponse], summary="크레인 아이템 목록 조회")
def list_crane_items(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results = db.scalars(
        select(CraneItem)
        .join(StandardCrane, CraneItem.standard_crane_id == StandardCrane.id)
        .where(StandardCrane.project_id == project_id)
        .offset(skip)
        .limit(limit)
    ).all()
    return results


@router.post("/cranes/items", response_model=CraneItemResponse, status_code=status.HTTP_201_CREATED, summary="크레인 아이템 생성")
def create_crane_item(item_in: CraneItemCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_crane_item.create(db, obj_in=item_in)
    response.headers["Location"] = f"/api/v1/cranes/items/{obj.id}"
    return obj
