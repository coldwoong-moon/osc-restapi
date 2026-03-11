from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.crud.misc import carry_in_request as crud_carry_in
from app.crud.misc import marker as crud_marker
from app.crud.misc import partner as crud_partner
from app.db.session import get_db
from app.models.carry_in import CarryInRequest
from app.models.construction import ConstructionPlan, ConstructionDueDate
from app.models.misc import Households, Marker, ModelEnvironment, ModelScene, Partner
from app.schemas.misc import (
    CarryInRequestCreate,
    CarryInRequestResponse,
    HouseholdsResponse,
    InstallCompletedResponse,
    MarkerCreate,
    MarkerResponse,
    MarkerUpdate,
    ModelEnvironmentResponse,
    ModelSceneResponse,
    PartnerCreate,
    PartnerResponse,
    ProductionCompletedResponse,
)
from app.models.production import ProductionCompleted, InstallCompleted

router = APIRouter(tags=["Misc"])


@router.get("/projects/{project_id}/constructions", summary="시공 계획 목록 조회")
def list_constructions(project_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    plans = db.scalars(select(ConstructionPlan).where(ConstructionPlan.project_id == project_id)).all()
    due_dates = db.scalars(select(ConstructionDueDate).where(ConstructionDueDate.project_id == project_id)).all()
    return {"plans": [{"id": p.id, "guid": p.guid, "name": p.name, "project_id": p.project_id} for p in plans],
            "due_dates": [{"id": d.id, "name": d.name, "begin_date": d.begin_date, "end_date": d.end_date, "project_id": d.project_id} for d in due_dates]}


@router.get("/projects/{project_id}/households", response_model=list[HouseholdsResponse], summary="세대 목록 조회")
def list_households(project_id: int, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results = db.scalars(
        select(Households).where(Households.project_id == project_id).offset(skip).limit(limit)
    ).all()
    return results


@router.get("/projects/{project_id}/map-markers", response_model=list[MarkerResponse], summary="지도 마커 목록 조회")
def list_map_markers(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_marker.get_multi(db, skip=skip, limit=limit, filters={"project_id": project_id})
    return results


@router.post("/projects/{project_id}/map-markers", response_model=MarkerResponse, status_code=status.HTTP_201_CREATED, summary="지도 마커 생성")
def create_map_marker(project_id: int, marker_in: MarkerCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = Marker(
        name=marker_in.name,
        guid=marker_in.guid,
        latitude=marker_in.latitude,
        longitude=marker_in.longitude,
        description=marker_in.description,
        project_id=project_id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    response.headers["Location"] = f"/api/v1/projects/{project_id}/map-markers/{obj.id}"
    return obj


@router.put("/map-markers/{marker_id}", response_model=MarkerResponse, summary="지도 마커 수정")
def update_map_marker(marker_id: int, marker_in: MarkerUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_marker.get(db, marker_id)
    if not obj:
        raise NotFoundException("Marker", marker_id)
    return crud_marker.update(db, db_obj=obj, obj_in=marker_in)


@router.delete("/map-markers/{marker_id}", status_code=status.HTTP_204_NO_CONTENT, summary="지도 마커 삭제")
def delete_map_marker(marker_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_marker.get(db, marker_id)
    if not obj:
        raise NotFoundException("Marker", marker_id)
    db.delete(obj)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/partners", response_model=list[PartnerResponse], summary="협력사 목록 조회")
def list_partners(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_partner.get_multi(db, skip=skip, limit=limit)
    return results


@router.post("/partners", response_model=PartnerResponse, status_code=status.HTTP_201_CREATED, summary="협력사 생성")
def create_partner(partner_in: PartnerCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_partner.create(db, obj_in=partner_in)
    response.headers["Location"] = f"/api/v1/partners/{obj.id}"
    return obj


@router.get("/projects/{project_id}/carry-in-requests", response_model=list[CarryInRequestResponse], summary="반입 요청 목록 조회")
def list_carry_in_requests(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_carry_in.get_multi(db, skip=skip, limit=limit, filters={"project_id": project_id})
    return results


@router.post("/projects/{project_id}/carry-in-requests", response_model=CarryInRequestResponse, status_code=status.HTTP_201_CREATED, summary="반입 요청 생성")
def create_carry_in_request(project_id: int, req_in: CarryInRequestCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = CarryInRequest(
        title=req_in.title,
        guid=req_in.guid,
        status=req_in.status,
        request_date=req_in.request_date,
        project_id=project_id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    response.headers["Location"] = f"/api/v1/projects/{project_id}/carry-in-requests/{obj.id}"
    return obj


@router.get("/projects/{project_id}/production-completed", response_model=list[ProductionCompletedResponse], summary="생산 완료 목록 조회")
def list_production_completed(project_id: int, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results = db.scalars(
        select(ProductionCompleted).where(ProductionCompleted.project_id == project_id).offset(skip).limit(limit)
    ).all()
    return results


@router.get("/projects/{project_id}/install-completed", response_model=list[InstallCompletedResponse], summary="설치 완료 목록 조회")
def list_install_completed(project_id: int, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results = db.scalars(
        select(InstallCompleted).where(InstallCompleted.project_id == project_id).offset(skip).limit(limit)
    ).all()
    return results


@router.get("/projects/{project_id}/model-environments", response_model=list[ModelEnvironmentResponse], summary="모델 환경 목록 조회")
def list_model_environments(project_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results = db.scalars(select(ModelEnvironment).where(ModelEnvironment.project_id == project_id)).all()
    return results


@router.get("/projects/{project_id}/model-scenes", response_model=list[ModelSceneResponse], summary="모델 씬 목록 조회")
def list_model_scenes(project_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results = db.scalars(select(ModelScene).where(ModelScene.project_id == project_id)).all()
    return results
