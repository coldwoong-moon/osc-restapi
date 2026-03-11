from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.crud.location import floor as crud_floor
from app.db.session import get_db
from app.schemas.location import FloorCreate, FloorResponse, FloorUpdate

router = APIRouter(prefix="/projects/{project_id}/floors", tags=["Floors"])


@router.get("", response_model=list[FloorResponse], summary="층 목록 조회")
def list_floors(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_floor.get_multi(db, skip=skip, limit=limit, filters={"project_id": project_id})
    return results


@router.post("", response_model=FloorResponse, status_code=status.HTTP_201_CREATED, summary="층 생성")
def create_floor(project_id: int, floor_in: FloorCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    from app.models.location import Floor
    obj = Floor(name=floor_in.name, aptcmpl_id=floor_in.aptcmpl_id, project_id=project_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    response.headers["Location"] = f"/api/v1/projects/{project_id}/floors/{obj.id}"
    return obj


@router.put("/{floor_id}", response_model=FloorResponse, summary="층 수정")
def update_floor(project_id: int, floor_id: int, floor_in: FloorUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_floor.get(db, floor_id)
    if not obj or obj.project_id != project_id:
        raise NotFoundException("Floor", floor_id)
    return crud_floor.update(db, db_obj=obj, obj_in=floor_in)


@router.delete("/{floor_id}", status_code=status.HTTP_204_NO_CONTENT, summary="층 삭제")
def delete_floor(project_id: int, floor_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_floor.get(db, floor_id)
    if not obj or obj.project_id != project_id:
        raise NotFoundException("Floor", floor_id)
    db.delete(obj)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
