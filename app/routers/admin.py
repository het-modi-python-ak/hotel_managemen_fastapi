from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database.database import get_db
from app.models.user import User
from app.models.role import Role
from typing import Annotated


SessionDep = Annotated[AsyncSession, Depends(get_db)]

router = APIRouter()

@router.post("/assign-role")
async def assign_role(user_id: int, role_id: int, db: SessionDep):
    
    user_result = await db.execute(
        select(User)
        .filter(User.id == user_id)
        .options(selectinload(User.roles)) 
    )
    user = user_result.scalars().first()

   
    role_result = await db.execute(
        select(Role).filter(Role.id == role_id)
    )
    role = role_result.scalars().first()

   
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role in user.roles:
        return {"message": "User already has this role"}

   
    user.roles.append(role)
    await db.commit()

    return {"message": f"Role '{role.name}' assigned to user '{user.name}'"}
