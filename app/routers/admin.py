from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import SessionLocal,get_db
from app.models.user import User
from app.models.role import Role
from typing import Annotated

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_db)]

@router.post("/assign-role")
def assign_role(user_id: int, role_id: int, db: SessionDep):

    user = db.query(User).filter(User.id == user_id).first()
    role = db.query(Role).filter(Role.id == role_id).first()

    user.roles.append(role)

    db.commit()

    return {"message": "Role assigned"}
