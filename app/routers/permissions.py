from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database.database import get_db
from app.models.permission import Permission
from app.models.role import Role
from typing import Annotated


SessionDep = Annotated[AsyncSession, Depends(get_db)]

router = APIRouter()

@router.post("/")
async def create_permission(name: str, db: SessionDep):
    permission = Permission(name=name)
    db.add(permission)
    await db.commit()
    await db.refresh(permission)
    return permission

@router.get("/")
async def get_permissions(db: SessionDep):
    result = await db.execute(select(Permission))
    permissions = result.scalars().all()
    return [
        {"id": p.id, "name": p.name} 
        for p in permissions
    ]

@router.post("/assign_permission")
async def assign_permission(role_id: int, permission_id: int, db: SessionDep):
   
    role_result = await db.execute(
        select(Role).filter(Role.id == role_id).options(selectinload(Role.permissions))
    )
    role = role_result.scalars().first()
    
    perm_result = await db.execute(
        select(Permission).filter(Permission.id == permission_id)
    )
    permission = perm_result.scalars().first()

    if not role or not permission:
        raise HTTPException(status_code=404, detail="Role or Permission not found")

    role.permissions.append(permission)
    await db.commit()

    return {"message": "Permission assigned"}

@router.get("/{permission_id}/roles")
async def get_roles_by_permission(permission_id: int, db: SessionDep):
 
    result = await db.execute(
        select(Permission)
        .filter(Permission.id == permission_id)
        .options(selectinload(Permission.roles))
    )
    permission = result.scalars().first()
    
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    return [
        {"id": role.id, "name": role.name}
        for role in permission.roles  
    ]
