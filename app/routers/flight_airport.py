from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.database.database import get_db
from app.models.flight_models import Airport 
from app.core.dependencies import get_current_user
from app.schemas.schemas import CreateAirport
from typing import Annotated, List
from app.models.user import User
from app.schemas.schemas import AirportResponse
# Use AsyncSession
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurretUser = Annotated[User, Depends(get_current_user)]

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED) 
async def create_airport(
    data: CreateAirport,
    db: SessionDep,
    current_user: CurretUser
):
    try:
        # Check if airport code already exists (Async style)
        result = await db.execute(select(Airport).filter(Airport.code == data.code.upper()))
        existing_airport = result.scalars().first()

        if existing_airport:
            raise HTTPException(status_code=400, detail="Airport code already exists")

        airport = Airport(
            code=data.code.upper(),
            name=data.name,
            location=data.location,
            country=data.country,
            created_by=current_user.id
        )
        
        db.add(airport)
        await db.commit()
        await db.refresh(airport)

        return airport
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error creating airport")
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/", response_model=List[AirportResponse])
async def get_airports(db: SessionDep):
    result = await db.execute(select(Airport))
    return result.scalars().all()

@router.get("/{airport_code}")
async def get_airport(airport_code: str, db: SessionDep):
    result = await db.execute(select(Airport).filter(Airport.code == airport_code.upper()))
    airport = result.scalars().first()
    
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    return airport
