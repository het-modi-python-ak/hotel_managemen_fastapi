from fastapi import APIRouter, Depends, HTTPException
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

# get all roles
@router.get("/")
def get_roles(db: Session = Depends(get_db)):
    role = db.query(Role).all()
    return role

# get users with their roles
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

# get a single role by ID
@router.get("/{role_id}")
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

# update a role by ID
@router.put("/{role_id}")
def update_role(role_id: int, name: str, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    role.name = name
    db.commit()
    db.refresh(role)
    return role

# delete a role by ID
@router.delete("/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    db.delete(role)
    db.commit()
    return {"message": f"Role with id {role_id} deleted successfully"}

