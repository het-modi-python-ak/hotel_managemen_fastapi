from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.role import Role

router = APIRouter()


@router.post("/roles")
def create_role(name: str, db: Session = Depends(get_db)):

    role = Role(name=name)

    db.add(role)
    db.commit()
    db.refresh(role)

    return role