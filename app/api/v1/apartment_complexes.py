from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.crud.location import apartment_complex as crud_apt
from app.db.session import get_db
from app.schemas.location import ApartmentComplexCreate, ApartmentComplexResponse, ApartmentComplexUpdate

router = APIRouter(prefix="/projects/{project_id}/apartment-complexes", tags=["Apartment Complexes"])


@router.get("", response_model=list[ApartmentComplexResponse], summary="단지 목록 조회")
def list_apartment_complexes(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_apt.get_multi(db, skip=skip, limit=limit, filters={"project_id": project_id})
    return results


@router.post("", response_model=ApartmentComplexResponse, status_code=status.HTTP_201_CREATED, summary="단지 생성")
def create_apartment_complex(project_id: int, apt_in: ApartmentComplexCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    from app.models.location import ApartmentComplex
    obj = ApartmentComplex(name=apt_in.name, guid=apt_in.guid, project_id=project_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    response.headers["Location"] = f"/api/v1/projects/{project_id}/apartment-complexes/{obj.id}"
    return obj


@router.put("/{apt_id}", response_model=ApartmentComplexResponse, summary="단지 수정")
def update_apartment_complex(project_id: int, apt_id: int, apt_in: ApartmentComplexUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_apt.get(db, apt_id)
    if not obj or obj.project_id != project_id:
        raise NotFoundException("ApartmentComplex", apt_id)
    return crud_apt.update(db, db_obj=obj, obj_in=apt_in)


@router.delete("/{apt_id}", status_code=status.HTTP_204_NO_CONTENT, summary="단지 삭제")
def delete_apartment_complex(project_id: int, apt_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_apt.get(db, apt_id)
    if not obj or obj.project_id != project_id:
        raise NotFoundException("ApartmentComplex", apt_id)
    db.delete(obj)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
