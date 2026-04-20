from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.permission import Permission
from app.models.role import Role
from app.models.permission import Permission
from typing import Annotated
SessionDep = Annotated[Session, Depends(get_db)]


router = APIRouter()

router = APIRouter()


@router.post("/")
def create_permission(name: str, db: SessionDep):

    permission = Permission(name=name)

    db.add(permission)
    db.commit()
    db.refresh(permission)

    return permission



@router.get("/")
def get_permissions(db: SessionDep):
    permissions = db.query(Permission).all()
    return [
        {
            "id": p.id, 
            "name": p.name
        } 
        for p in permissions
    ]




@router.post("/assign_permission")
def assign_permission(role_id: int, permission_id: int, db: SessionDep):

    role = db.query(Role).filter(Role.id == role_id).first()
    permission = db.query(Permission).filter(Permission.id == permission_id).first()

    role.permissions.append(permission)

    db.commit()

    return {"message": "Permission assigned"}


@router.get("/{permission_id}/roles")
def get_roles_by_permission(permission_id: int, db: SessionDep):
    """
    Returns a list of all roles that have been granted a specific permission.
    """
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    return [
        {
            "id": role.id,
            "name": role.name
        }
        for role in permission.roles  
    ]