from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload  # Critical for relationships
from app.database.database import get_db
from app.models.role import Role
from app.models.user import User
from typing import Annotated


SessionDep = Annotated[AsyncSession, Depends(get_db)]

router = APIRouter()

@router.post("/")
async def create_role(name: str, db: SessionDep):
    role = Role(name=name)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role

@router.get("/")
async def get_roles(db: SessionDep):
    result = await db.execute(select(Role))
    return result.scalars().all()

@router.get("/users")
async def get_users(db: SessionDep):
    
    query = select(User).options(selectinload(User.roles))
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [
        {
            "user_id": user.id,
            "username": user.name,
            "roles": [
                {"id": r.id, "name": r.name}
                for r in user.roles
            ]
        }
        for user in users
    ]

@router.get("/{role_id}")
async def get_role(role_id: int, db: SessionDep):
    result = await db.execute(select(Role).filter(Role.id == role_id))
    role = result.scalars().first()
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.patch("/{role_id}")
async def update_role(role_id: int, name: str, db: SessionDep):
    result = await db.execute(select(Role).filter(Role.id == role_id))
    role = result.scalars().first()
    
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    role.name = name
    await db.commit()
    await db.refresh(role)
    return role

@router.delete("/{role_id}")
async def delete_role(role_id: int, db: SessionDep):
    result = await db.execute(select(Role).filter(Role.id == role_id))
    role = result.scalars().first()
    
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    await db.delete(role)
    await db.commit()
    return {"message": f"Role with id {role_id} deleted successfully"}
