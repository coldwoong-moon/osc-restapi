from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.exceptions import BadRequestException, ConflictException, NotFoundException
from app.crud.user import user as crud_user
from app.db.session import get_db
from app.models.user import Role, User
from app.schemas.user import PasswordUpdate, RoleResponse, UserCreate, UserResponse, UserUpdate

router = APIRouter(tags=["Users"])


@router.get("/users", response_model=list[UserResponse], summary="사용자 목록 조회")
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results, _ = crud_user.get_multi(db, skip=skip, limit=limit)
    return results


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="사용자 생성")
def create_user(user_in: UserCreate, response: Response, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    existing = db.scalar(select(User).where(User.email == user_in.email))
    if existing:
        raise ConflictException(f"User with email '{user_in.email}' already exists")
    obj = crud_user.create(db, obj_in=user_in)
    response.headers["Location"] = f"/api/v1/users/{obj.id}"
    return obj


@router.get("/users/{user_id}", response_model=UserResponse, summary="사용자 상세 조회")
def get_user(user_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_user.get(db, user_id)
    if not obj:
        raise NotFoundException("User", user_id)
    return obj


@router.put("/users/{user_id}", response_model=UserResponse, summary="사용자 수정")
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_user.get(db, user_id)
    if not obj:
        raise NotFoundException("User", user_id)
    return crud_user.update(db, db_obj=obj, obj_in=user_in)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="사용자 삭제")
def delete_user(user_id: int, db: Session = Depends(get_db), user: dict = Depends(require_role("ROLE_ADMIN"))):
    obj = crud_user.get(db, user_id)
    if not obj:
        raise NotFoundException("User", user_id)
    db.delete(obj)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/users/{user_id}/password", summary="비밀번호 변경")
def update_password(user_id: int, payload: PasswordUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    obj = crud_user.get(db, user_id)
    if not obj:
        raise NotFoundException("User", user_id)
    if obj.password != payload.password:
        raise BadRequestException("Current password does not match")
    obj.password = payload.new_password
    db.commit()
    return {"message": "Password updated"}


@router.get("/roles", response_model=list[RoleResponse], summary="역할 목록 조회")
def list_roles(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    results = db.scalars(select(Role)).all()
    return results
