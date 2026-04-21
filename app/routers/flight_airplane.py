from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.database.database import get_db
from app.models.flight_models import Airplane, Airline, AirplaneSeat
from app.core.dependencies import get_current_user
from pydantic import BaseModel
from app.schemas.schemas import SeatCategory, CreateAirplane
from typing import Annotated, List
from app.models.user import User

# Use AsyncSession
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurretUser = Annotated[User, Depends(get_current_user)]

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_airplane(
    data: CreateAirplane,
    db: SessionDep,
    current_user: CurretUser
):
    # Validation Logic
    if data.total_seats <= 0:
        raise HTTPException(status_code=400, detail="Total seats must be > 0")

    if (data.total_business_seat + data.total_economy_seat + data.total_premium_seat) != data.total_seats:
        raise HTTPException(status_code=412, detail="Seat category totals must equal total seats")

    try:
        # Check Airline Ownership
        airline_result = await db.execute(
            select(Airline).filter(
                Airline.airline_id == data.airline_id,
                Airline.created_by == current_user.id
            )
        )
        airline = airline_result.scalars().first()

        if not airline:
            raise HTTPException(status_code=403, detail="Unauthorized airline access")

        # 3. Create Airplane
        airplane = Airplane(
            model=data.model,
            total_seats=data.total_seats,
            airline_id=data.airline_id,
            created_by=current_user.id
        )

        db.add(airplane)
        await db.flush()  # airplane.airplane_id without committing

        #  Generate Seat Layout
        seats = []
        #  seat numbering
        categories = [
            (data.total_business_seat, "B", SeatCategory.BUSINESS.value),
            (data.total_premium_seat, "P", SeatCategory.PREMIUM.value),
            (data.total_economy_seat, "E", SeatCategory.ECONOMY.value)
        ]

        for count, prefix, s_class in categories:
            for i in range(count):
                seats.append(
                    AirplaneSeat(
                        airplane_id=airplane.airplane_id,
                        seat_number=f"{prefix}{i+1}",
                        seat_class=s_class,
                        created_by=current_user.id
                    )
                )

        db.add_all(seats)
        await db.commit()
        await db.refresh(airplane)

        return {
            "message": "Airplane created successfully with seat layout",
            "airplane_id": airplane.airplane_id,
            "total_seats_created": len(seats)
        }

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_all_airplanes(db: SessionDep):
    result = await db.execute(select(Airplane))
    airplanes = result.scalars().all()
    if not airplanes:
        raise HTTPException(status_code=404, detail="No airplanes found")
    return airplanes

@router.get("/{airplane_id}")
async def get_airplane(airplane_id: int, db: SessionDep):
    result = await db.execute(select(Airplane).filter(Airplane.airplane_id == airplane_id))
    airplane = result.scalars().first()
    if not airplane:
        raise HTTPException(status_code=404, detail="Airplane not found")
    return airplane

class UpdateAirplane(BaseModel):
    airplane_id: int
    model: str | None = None
    total_seats: int | None = None



@router.patch("/{airplane_id}")
async def update_airplane(
    data: UpdateAirplane,
    db: SessionDep,
    current_user: CurretUser
):
    try:
        result = await db.execute(
            select(Airplane).filter(
                Airplane.airplane_id == data.airplane_id,
                Airplane.created_by == current_user.id
            )
        )
        airplane = result.scalars().first()
        
        if not airplane:
            raise HTTPException(status_code=404, detail="Airplane not found")

        if data.total_seats is not None and data.total_seats <= 0:
            raise HTTPException(status_code=400, detail="Total seats must be > 0")

        if data.model:
            airplane.model = data.model
        if data.total_seats:
            airplane.total_seats = data.total_seats

        await db.commit()
        await db.refresh(airplane)
        return airplane
    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail="Update failed")



@router.delete("/{airplane_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_airplane(airplane_id: int, db: SessionDep, current_user: CurretUser):
    try:
        result = await db.execute(
            select(Airplane).filter(
                Airplane.airplane_id == airplane_id,
                Airplane.created_by == current_user.id
            )
        )
        airplane = result.scalars().first()
        
        if not airplane:
            raise HTTPException(status_code=404, detail="Airplane not found")

        await db.delete(airplane)
        await db.commit()
        return None  
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Delete failed")
