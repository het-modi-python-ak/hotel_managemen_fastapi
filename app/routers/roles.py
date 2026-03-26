from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.role import Role
from models.user import User

router = APIRouter()


@router.post("/")
def create_role(name: str, db: Session = Depends(get_db)):

    role = Role(name=name)

    db.add(role)
    db.commit()
    db.refresh(role)

    return role



@router.get("/users")
def get_users(db: Session = Depends(get_db)):

    users = db.query(User).all()

    result = []

    for user in users:
        result.append({
            "user_id": user.id,
            "username": user.name,
            "roles": [
                {
                    "id": r.id,
                    "name": r.name
                }
                for r in user.roles
            ]
        })

    return result

