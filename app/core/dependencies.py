from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database.database import get_db
from app.models.user import User
import os
from dotenv import load_dotenv
from app.models.role import Role

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id") 
        
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Async query to fetch the user
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise credentials_exception 
    
    return user

def require_permission(permission_name: str):
    
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        stmt = (
            select(User)
            .filter(User.id == current_user.id)
            .options(
                selectinload(User.roles)
                .selectinload(Role.permissions) 
            )
        )
        result = await db.execute(stmt)
        user_with_perms = result.scalars().first()

        for role in user_with_perms.roles:
            for perm in role.permissions:
                if perm.name == permission_name:
                    return True

        raise HTTPException(status_code=403, detail="Permission denied")

    return permission_checker
