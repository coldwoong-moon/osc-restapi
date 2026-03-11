from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.crud.project import project as crud_project, project_model as crud_project_model
from app.db.session import get_db
from app.models.project import ProjectUser
from app.schemas.project import (
    ProjectCreate,
    ProjectModelCreate,
    ProjectModelResponse,
    ProjectModelUpdate,
    ProjectResponse,
    ProjectUpdate,
    ProjectUserCreate,
    ProjectUserResponse,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectResponse], summary="프로젝트 목록 조회")
def list_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_project.get_multi(db, skip=skip, limit=limit, filters={"delete_status": False})
    return results


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED, summary="프로젝트 생성")
def create_project(project_in: ProjectCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_project.create(db, obj_in=project_in)
    response.headers["Location"] = f"/api/v1/projects/{obj.id}"
    return obj


@router.get("/{project_id}", response_model=ProjectResponse, summary="프로젝트 상세 조회")
def get_project(project_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_project.get(db, project_id)
    if not obj:
        raise NotFoundException("Project", project_id)
    return obj


@router.put("/{project_id}", response_model=ProjectResponse, summary="프로젝트 수정")
def update_project(project_id: int, project_in: ProjectUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_project.get(db, project_id)
    if not obj:
        raise NotFoundException("Project", project_id)
    return crud_project.update(db, db_obj=obj, obj_in=project_in)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, summary="프로젝트 삭제 (소프트)")
def delete_project(project_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_project.get(db, project_id)
    if not obj:
        raise NotFoundException("Project", project_id)
    obj.delete_status = True
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{project_id}/models", response_model=list[ProjectModelResponse], summary="프로젝트 모델 목록")
def list_project_models(project_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_project_model.get_multi(db, filters={"project_id": project_id})
    return results


@router.post("/{project_id}/models", response_model=ProjectModelResponse, status_code=status.HTTP_201_CREATED, summary="프로젝트 모델 생성")
def create_project_model(project_id: int, model_in: ProjectModelCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    model_in.project_id = project_id
    obj = crud_project_model.create(db, obj_in=model_in)
    response.headers["Location"] = f"/api/v1/projects/{project_id}/models/{obj.id}"
    return obj


@router.get("/{project_id}/users", response_model=list[ProjectUserResponse], summary="프로젝트 사용자 목록")
def list_project_users(project_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results = db.scalars(select(ProjectUser).where(ProjectUser.project_id == project_id)).all()
    return results


@router.post("/{project_id}/users", response_model=ProjectUserResponse, status_code=status.HTTP_201_CREATED, summary="프로젝트 사용자 할당")
def add_project_user(project_id: int, user_in: ProjectUserCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = ProjectUser(project_id=project_id, user_id=user_in.user_id, role_id=user_in.role_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{project_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="프로젝트 사용자 제거")
def remove_project_user(project_id: int, user_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = db.scalars(
        select(ProjectUser).where(ProjectUser.project_id == project_id, ProjectUser.user_id == user_id)
    ).first()
    if not obj:
        raise NotFoundException("ProjectUser", f"{project_id}/{user_id}")
    db.delete(obj)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
