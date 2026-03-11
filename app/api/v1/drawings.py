from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.crud.drawing import drawing as crud_drawing
from app.crud.drawing import drawing_tree as crud_drawing_tree
from app.crud.drawing import reference_drawing as crud_reference_drawing
from app.db.session import get_db
from app.models.drawing import DrawingTree, ReferenceDrawing
from app.schemas.drawing import (
    DrawingCreate,
    DrawingResponse,
    DrawingTreeCreate,
    DrawingTreeResponse,
    DrawingTreeUpdate,
    ReferenceDrawingCreate,
    ReferenceDrawingResponse,
)

router = APIRouter(tags=["Drawings"])


@router.get("/projects/{project_id}/drawings/trees", response_model=list[DrawingTreeResponse], summary="도면 트리 목록 조회")
def list_drawing_trees(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_drawing_tree.get_multi(db, skip=skip, limit=limit, filters={"project_id": project_id})
    return results


@router.post("/projects/{project_id}/drawings/trees", response_model=DrawingTreeResponse, status_code=status.HTTP_201_CREATED, summary="도면 트리 생성")
def create_drawing_tree(project_id: int, tree_in: DrawingTreeCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = DrawingTree(
        name=tree_in.name,
        guid=tree_in.guid,
        drawing_div=tree_in.drawing_division,
        depth=tree_in.depth,
        parent_id=tree_in.parent_id,
        project_id=project_id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    response.headers["Location"] = f"/api/v1/projects/{project_id}/drawings/trees/{obj.id}"
    return obj


@router.put("/drawings/trees/{tree_id}", response_model=DrawingTreeResponse, summary="도면 트리 수정")
def update_drawing_tree(tree_id: int, tree_in: DrawingTreeUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_drawing_tree.get(db, tree_id)
    if not obj:
        raise NotFoundException("DrawingTree", tree_id)
    update_data = tree_in.model_dump(exclude_unset=True)
    if "drawing_division" in update_data:
        update_data["drawing_div"] = update_data.pop("drawing_division")
    for field, value in update_data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/drawings/trees/{tree_id}", status_code=status.HTTP_204_NO_CONTENT, summary="도면 트리 삭제")
def delete_drawing_tree(tree_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_drawing_tree.get(db, tree_id)
    if not obj:
        raise NotFoundException("DrawingTree", tree_id)
    db.delete(obj)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/projects/{project_id}/drawings", response_model=list[DrawingResponse], summary="도면 목록 조회")
def list_drawings(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_drawing.get_multi(db, skip=skip, limit=limit, filters={"project_id": project_id})
    return results


@router.post("/projects/{project_id}/drawings", response_model=DrawingResponse, status_code=status.HTTP_201_CREATED, summary="도면 생성")
def create_drawing(project_id: int, drawing_in: DrawingCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    drawing_in.project_id = project_id
    obj = crud_drawing.create(db, obj_in=drawing_in)
    response.headers["Location"] = f"/api/v1/projects/{project_id}/drawings/{obj.id}"
    return obj


@router.get("/projects/{project_id}/reference-drawings", response_model=list[ReferenceDrawingResponse], summary="참조 도면 목록 조회")
def list_reference_drawings(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_reference_drawing.get_multi(db, skip=skip, limit=limit, filters={"project_id": project_id})
    return results


@router.post("/projects/{project_id}/reference-drawings", response_model=ReferenceDrawingResponse, status_code=status.HTTP_201_CREATED, summary="참조 도면 생성")
def create_reference_drawing(project_id: int, drawing_in: ReferenceDrawingCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = ReferenceDrawing(
        name=drawing_in.name,
        elevation=drawing_in.elevation,
        file_name=drawing_in.file_name,
        save_file_name=drawing_in.saved_file_name,
        project_id=project_id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    response.headers["Location"] = f"/api/v1/projects/{project_id}/reference-drawings/{obj.id}"
    return obj
