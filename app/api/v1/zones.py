from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.crud.location import zone as crud_zone
from app.db.session import get_db
from app.schemas.location import ZoneCreate, ZoneResponse, ZoneUpdate

router = APIRouter(prefix="/projects/{project_id}/zones", tags=["Zones"])


@router.get("", response_model=list[ZoneResponse], summary="구역 목록 조회")
def list_zones(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_zone.get_multi(db, skip=skip, limit=limit, filters={"project_id": project_id})
    return results


@router.post("", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED, summary="구역 생성")
def create_zone(project_id: int, zone_in: ZoneCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    from app.models.location import Zone
    obj = Zone(
        name=zone_in.name,
        guid=zone_in.guid,
        end_date=zone_in.end_date,
        color=zone_in.color,
        polygon_point=zone_in.points,
        project_id=project_id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    response.headers["Location"] = f"/api/v1/projects/{project_id}/zones/{obj.id}"
    return obj


@router.put("/{zone_id}", response_model=ZoneResponse, summary="구역 수정")
def update_zone(project_id: int, zone_id: int, zone_in: ZoneUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_zone.get(db, zone_id)
    if not obj or obj.project_id != project_id:
        raise NotFoundException("Zone", zone_id)
    update_data = zone_in.model_dump(exclude_unset=True)
    if "points" in update_data:
        update_data["polygon_point"] = update_data.pop("points")
    for field, value in update_data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT, summary="구역 삭제")
def delete_zone(project_id: int, zone_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_zone.get(db, zone_id)
    if not obj or obj.project_id != project_id:
        raise NotFoundException("Zone", zone_id)
    db.delete(obj)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
