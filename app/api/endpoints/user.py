from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.db.database import get_db
# from app.schemas.user import UserCreate, User
# from app.models.user import User as UserModel

router = APIRouter()

@router.get("/login")
def read_user(user_id: str, user_password: str):
    return {"test":"123"}
    # db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    # if db_user is None:
    #     raise HTTPException(status_code=404, detail="User not found")
    # return db_user

# @router.post("/", response_model=User)
# def create_user(user: UserCreate, db: Session = Depends(get_db)):
#     db_user = UserModel(email=user.email, hashed_password=user.password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# @router.get("/{user_id}", response_model=User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user