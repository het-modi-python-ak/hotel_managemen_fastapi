from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.permission import Permission
from models.role import Role
from models.permission import Permission

router = APIRouter()


@router.post("/permissions")
def create_permission(name: str, db: Session = Depends(get_db)):

    permission = Permission(name=name)

    db.add(permission)
    db.commit()
    db.refresh(permission)

    return permission





@router.post("/assign-permission")
def assign_permission(role_id: int, permission_id: int, db: Session = Depends(get_db)):

    role = db.query(Role).filter(Role.id == role_id).first()
    permission = db.query(Permission).filter(Permission.id == permission_id).first()

    role.permissions.append(permission)

    db.commit()

    return {"message": "Permission assigned"}