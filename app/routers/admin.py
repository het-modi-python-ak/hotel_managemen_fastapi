from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import SessionLocal,get_db
from app.models.user import User
from app.models.role import Role


router = APIRouter()



@router.post("/assign-role")
def assign_role(user_id: int, role_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()
    role = db.query(Role).filter(Role.id == role_id).first()

    user.roles.append(role)

    db.commit()

    return {"message": "Role assigned"}
