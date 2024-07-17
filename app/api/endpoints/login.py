from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import bcrypt


from app.db.manager import get_db_connection
from app.models.user import User
from app.models.authority import Authority


class LoginInfo(BaseModel):
    email: str
    password: str


router = APIRouter()


@router.post("")
def login_user(login_info: LoginInfo, db: Session = Depends(get_db_connection)):
    user = db.query(User).filter(User.email == login_info.email).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="로그인 정보가 올바르지 않습니다. id와 password를 확인하세요.",
        )

    # bcrypt.checkpw 함수는 데이터베이스 수준에서 실행할 수 없음.
    if bcrypt.checkpw(login_info.password.encode("utf-8"), user.password) is False:
        raise HTTPException(
            status_code=401,
            detail="로그인 정보가 올바르지 않습니다. id와 password를 확인하세요.",
        )

    authority = db.query(Authority).filter(Authority.id == login_info.email).first()

    if authority is None:
        raise HTTPException(
            status_code=401,
            detail="역할 정보가 올바르지 않습니다. 관리자에게 문의하세요.",
        )

    return {
        "id": user.id,
        "name": user.name,
        "partnerId": user.partner_id,
        "department": user.dept,
        "rank": user.rank,
        "tel": user.telno,
        "mobile": user.mbtlnum,
        "roleId": authority.authorityName,
        "auth": "A" if authority.authorityName == "ROLE_ADMIN" else "U",
        "username": user.name,
    }
