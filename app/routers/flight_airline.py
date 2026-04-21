from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.database.database import get_db
from app.models.flight_models import Airline
from app.core.dependencies import get_current_user, require_permission
from pydantic import BaseModel
from app.schemas.schemas import CreateArline
from typing import Annotated, List
from app.models.user import User

SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurretUser = Annotated[User, Depends(get_current_user)]

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_airline(
    data: CreateArline,
    db: SessionDep,
    current_user: CurretUser,
    
    user=Depends(require_permission("add_airlines"))
):
    try:
       
        result = await db.execute(select(Airline).filter(Airline.name == data.name))
        existing_airline = result.scalars().first()
        
        if existing_airline:
            raise HTTPException(status_code=400, detail="Airline already exists")

        airline = Airline(
            name=data.name, 
            country=data.country, 
            created_by=current_user.id 
        )
        db.add(airline)
        await db.commit()
        await db.refresh(airline)
        return airline
    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



@router.get("/")
async def get_all_airlines(db: SessionDep):
    result = await db.execute(select(Airline))
    airlines = result.scalars().all()
    if not airlines:
        raise HTTPException(status_code=404, detail="No airlines found")
    return airlines




@router.get("/my")
async def get_my_airlines(db: SessionDep, current_user: CurretUser):
    result = await db.execute(
        select(Airline).filter(Airline.created_by == current_user.id)
    )
    airlines = result.scalars().all()
    if not airlines:
        raise HTTPException(status_code=404, detail="No airlines found")
    return airlines


@router.get("/{airline_id}")
async def get_airline(airline_id: int, db: SessionDep):
    result = await db.execute(select(Airline).filter(Airline.airline_id == airline_id))
    airline = result.scalars().first()
    if not airline:
        raise HTTPException(status_code=404, detail="Airline not found")
    return airline

class UpdateArline(BaseModel):
    airline_id: int
    name: str | None = None
    country: str | None = None

@router.patch("/{airline_id}")
async def update_airline(
    data: UpdateArline,
    db: SessionDep,
    current_user: CurretUser
):
    try:
        # Fetch current airline
        result = await db.execute(
            select(Airline).filter(
                Airline.airline_id == data.airline_id,
                Airline.created_by == current_user.id
            )
        )
        airline = result.scalars().first()
        
        if not airline:
            raise HTTPException(status_code=404, detail="Airline not found or unauthorized")

        if data.name:
            # Check for duplicate names excluding current ID
            dup_result = await db.execute(
                select(Airline).filter(Airline.name == data.name, Airline.airline_id != data.airline_id)
            )
            if dup_result.scalars().first():
                raise HTTPException(status_code=400, detail="Airline name already exists")
            airline.name = data.name
        
        if data.country:
            airline.country = data.country

        await db.commit()
        await db.refresh(airline)
        return airline
    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail="Update failed")




@router.delete("/{airline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_airline(airline_id: int, db: SessionDep, current_user: CurretUser):
    try:
        result = await db.execute(
            select(Airline).filter(
                Airline.airline_id == airline_id,
                Airline.created_by == current_user.id
            )
        )
        airline = result.scalars().first()
        
        if not airline:
            raise HTTPException(status_code=404, detail="Airline not found")

        await db.delete(airline)
        await db.commit()
        return None 
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Delete failed")
