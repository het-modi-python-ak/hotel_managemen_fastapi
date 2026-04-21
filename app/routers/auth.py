from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import Annotated
from pydantic import BaseModel, Field

from app.database.database import get_db
from app.models.user import User
from app.models.role import Role 

from app.core.security import hash_password, verify_password, create_access_token, generate_email_token
from app.core.dependencies import get_current_user
from app.core.redis_client import redis_client
from app.services.email_service import send_verification_email
from fastapi.security.oauth2 import OAuth2PasswordRequestForm


SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter()

class CreateUser(BaseModel):
    name: str
    email: str
    phone: str = Field(..., pattern=r'^\d{10}$', description="10-digit phone number")
    password: str


@router.post("/signup")
async def signup(background_tasks: BackgroundTasks, data: CreateUser, db: SessionDep):
    try:
        result = await db.execute(select(User).filter(User.email == data.email))
        existing_user = result.scalars().first()
        
        if existing_user:
            raise HTTPException(status_code=409, detail="Email already exists")

        new_user = User(
            name=data.name,
            email=data.email,
            phone=data.phone,
            password=hash_password(data.password),
            is_verified=False
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        token = generate_email_token()
        
        redis_client.setex(f"email_verify:{token}", 900, new_user.id)
        background_tasks.add_task(send_verification_email, new_user.email, token)

        return {"message": "Verification email sent"}
    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")



@router.get("/verify-email")
async def verify_email(token: str, db: SessionDep):
    try:
        user_id = redis_client.get(f"email_verify:{token}")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
        result = await db.execute(select(User).filter(User.id == int(user_id)))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_verified = True
        await db.commit()
        redis_client.delete(f"email_verify:{token}")
        return {"message": "Email verified successfully"}
    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/login")
async def login(data: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep):
    try:
        result = await db.execute(select(User).filter(User.email == data.username))
        user = result.scalars().first()
        
        if not user or not verify_password(data.password, user.password):
            raise HTTPException(status_code=400, detail="Invalid email or password")
        
        token = create_access_token({"user_id": user.id})
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail="Login error")



@router.get("/me")
async def read_user_me(current_user: CurrentUser):
    return {"id": current_user.id, "name": current_user.name, "email": current_user.email}



@router.post("/assign-role")
async def assign_role(user_id: int, role_id: int, db: SessionDep):
    try:
       
        user_result = await db.execute(
            select(User).filter(User.id == user_id).options(selectinload(User.roles))
        )
        user = user_result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

       
        role_result = await db.execute(select(Role).filter(Role.id == role_id))
        role = role_result.scalars().first()
        
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        if role not in user.roles:
            user.roles.append(role)
            await db.commit()
            return {"message": f"Role '{role.name}' assigned to {user.name}"}
        
        return {"message": "User already has this role"}
    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))
