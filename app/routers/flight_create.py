from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError # Added IntegrityError
from app.database.database import get_db
from app.models.flight_models import Flight, AirplaneSeat, Airplane, FlightSeat
from app.core.dependencies import get_current_user
from datetime import datetime
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
        #date validation
        if depart_time >= arrival_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arrival time must be after departure time."
            )
        
        if depart_time < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Departure time cannot be in the past."
            )

       #anoher plane
        airplane = db.query(Airplane).filter(
            Airplane.airplane_id == airplane_id,
            Airplane.created_by == current_user.id
        ).first()

        if not airplane:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot create a flight using another user's plane"
            )

       
        # We look for other flight
        overlapping_flight = db.query(Flight).filter(
            Flight.airplane_id == airplane_id,
           
            Flight.depart_time < arrival_time,
            Flight.arrival_time > depart_time
        ).first()

        if overlapping_flight:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Airplane {airplane_id} is already scheduled: {overlapping_flight.flight_number} "
                       f"({overlapping_flight.depart_time} to {overlapping_flight.arrival_time})"
            )

       
        airplane_seats = db.query(AirplaneSeat).filter(AirplaneSeat.airplane_id == airplane_id).all()
        if not airplane_seats:
            raise HTTPException(status_code=400, detail="Airplane seat layout not found")

        
        new_flight = Flight(
            flight_number=flight_number,
            airplane_id=airplane_id,
            source_id=source_id,
            destination_id=destination_id,
            depart_time=depart_time,
            arrival_time=arrival_time,
            created_by=current_user.id
        )
        db.add(new_flight)
        db.flush()  
        #
        seats = [
            FlightSeat(
                flight_id=new_flight.flight_id,
                seat_number=seat.seat_number,
                seat_class=seat.seat_class,
                price=1000,
                created_by=current_user.id
            )
            for seat in airplane_seats
        ]
        db.bulk_save_objects(seats)
        
        db.commit()

        return {"message": "Flight created successfully", "flight_id": new_flight.flight_id ,
                "source_id" : new_flight.source_id,"destination_id" : new_flight.destination_id}
        

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Flight number '{flight_number}' already exists."
        ) 
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/")
def get_all_flights(db: Session = Depends(get_db)):
    flights = db.query(Flight).all()
    if not flights:
        raise HTTPException(status_code=404, detail="No flights found")
    return flights




@router.get("/me")
def get_all_flights(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    flights = db.query(Flight).filter(Flight.created_by == current_user.id).all()
    if not flights:
        raise HTTPException(status_code=404, detail="No flights found")
    return flights



@router.delete("/{flight_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flight(
    flight_id: int, 
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    
    flight = db.query(Flight).filter(
        Flight.flight_id == flight_id, 
        Flight.created_by == current_user.id
    ).first()

    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found or unauthorized")

    try:
        
        db.query(FlightSeat).filter(FlightSeat.flight_id == flight_id).delete()
        
      
        db.delete(flight)

        db.commit()
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not delete flight: {str(e)}")


@router.get("/search_flight")
def search_flights(source_id:int,destination_id:int,db:Session=Depends(get_db)):
    try:
        flight  = db.query(Flight).filter(Flight.source_id==source_id,Flight.destination_id==destination_id).all()
        return flight
    except SQLAlchemyError as e:
        raise HTTPException(status_code=404,detail=f"sql database error {e}" )

        
