from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.database import get_db
from app.models.flight_models import Flight,AirplaneSeat,Airplane,FlightSeat
from app.core.dependencies import get_current_user
# from app.schemas.schemas import AirportUpdate,FlightCreate,FlightUpdate ,FlightResponse
from datetime import datetime,timezone
from typing import List





router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_flight(
    flight_number: str,
    airplane_id: int,
    source_id: int,
    destination_id: int,
    depart_time: datetime,
    arrival_time: datetime,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
       
        airplane = db.query(Airplane).filter(
            Airplane.airplane_id == airplane_id,
            Airplane.created_by == current_user.id
        ).first()

        if not airplane:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot create a flight using another user's plane"
            )
            
            
        #not able to book in the same time 
        existing_flight = db.query(Flight).filter(
    Flight.airplane_id == airplane_id,
    Flight.depart_time < arrival_time,
    Flight.arrival_time > depart_time
).first()

        if existing_flight:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Airplane {airplane_id} is already scheduled for flight {existing_flight.flight_number} between {existing_flight.depart_time} and {existing_flight.arrival_time}"
            )

        # 2. Fetch layout
        airplane_seats = db.query(AirplaneSeat).filter(
            AirplaneSeat.airplane_id == airplane_id
        ).all()

        if not airplane_seats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Airplane seat layout not found"
            )

        
        flight = Flight(
            flight_number=flight_number,
            airplane_id=airplane_id,
            source_id=source_id,
            destination_id=destination_id,
            depart_time=depart_time, 
            arrival_time=arrival_time,
            created_by=current_user.id
        )
        db.add(flight)
        db.flush() 

      
        seats = [
            FlightSeat(
                flight_id=flight.flight_id,
                seat_number=seat.seat_number,
                seat_class=seat.seat_class,
                price=1000,
                created_by=current_user.id
            )
            for seat in airplane_seats
        ]
        
        db.bulk_save_objects(seats) 
        db.commit() 
        
        return {
            "message": "Flight created successfully",
            "flight_id": flight.flight_id,
            "seats_generated": len(seats)
        }

    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating flight: {str(e)}"
        )          
            
            
            
#get
@router.get("/")
def get_all_flights(db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    flights = db.query(Flight).filter(Flight.created_by == current_user.id).all()
    
    if not flights:
        raise HTTPException(status_code=404,detail="No flight found")
    
    return flights



