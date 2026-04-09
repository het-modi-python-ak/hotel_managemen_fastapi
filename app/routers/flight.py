# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from app.database.database import get_db
# from app.models.flight_models import Flight,Airport
# from app.core.dependencies import get_current_user
# from app.schemas.schemas import AirportUpdate,FlightCreate,FlightUpdate ,FlightResponse
# from datetime import datetime,timezone
# from typing import List

# router = APIRouter()


# @router.post("/", status_code=status.HTTP_201_CREATED)
# def create_flight(
#     flight: FlightCreate,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     try:
        
#         if flight.source_id == flight.destination_id:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Source and destination cannot be the same"
#             )

       
#         now = datetime.now(timezone.utc)
#         if flight.depart_time <= now or flight.arrival_time <= now:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Flight times must be in the future"
#             )

       
#         if flight.arrival_time <= flight.depart_time:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Arrival time must be after departure time"
#             )

        
#         source_airport = db.query(Airport).filter(Airport.id == flight.source_id).first()
#         dest_airport = db.query(Airport).filter(Airport.id == flight.destination_id).first()

#         if not source_airport or not dest_airport:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Invalid airport ID"
#             )

        
#         existing_flight = db.query(Flight).filter(
#             Flight.flight_number == flight.flight_number
#         ).first()

#         if existing_flight:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Flight number already exists"
#             )

#         new_flight = Flight(
#             flight_number=flight.flight_number,
#             created_by=current_user.id,
#             source_id=flight.source_id,
#             destination_id=flight.destination_id,
#             depart_time=flight.depart_time,
#             arrival_time=flight.arrival_time
#         )
#         db.add(new_flight)
#         db.commit()
#         db.refresh(new_flight)

#         return new_flight

#     except HTTPException:
#         raise
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Database error occurred"
#         )
        
        
        
        
        
        
              
# @router.get("/", response_model=List[FlightResponse])
# def get_flights(db: Session = Depends(get_db)):
#     return db.query(Flight).all()

# @router.get("/{flight_id}")
# def get_flight(flight_id: int, db: Session = Depends(get_db)):
#     flight = db.query(Flight).filter(Flight.flight_id == flight_id).first()
#     if not flight:
#         raise HTTPException(status_code=404, detail="Flight not found")
#     return flight

# # PATCH: Update specific fields of a flight
# @router.patch("/{flight_id}")
# def update_flight(
#     flight_id: int, 
#     flight_updates: FlightUpdate, 
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     db_flight = db.query(Flight).filter(Flight.flight_id == flight_id).first()
#     if not db_flight:
#         raise HTTPException(status_code=404, detail="Flight not found")

    
#     update_data = flight_updates.model_dump(exclude_unset=True)
    
#     # date validation
#     now = datetime.now(timezone.utc)
#     if flight_updates.depart_time <= now or flight_updates.arrival_time <= now:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Flight times must be in the future"
#             )

       
#     if flight_updates.arrival_time <= flight_updates.depart_time:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Arrival time must be after departure time"
#             )

    
    
    
#     for key, value in update_data.items():
#         setattr(db_flight, key, value)

#     try:
#         db.commit()
#         db.refresh(db_flight)
#         return db_flight
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="Database error occurred")



# # DELETE:
# @router.delete("/{flight_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_flight(
#     flight_id: int, 
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     flight = db.query(Flight).filter(Flight.flight_id == flight_id,Flight.created_by==current_user.id).first()
#     if not flight:
#         raise HTTPException(status_code=404, detail="Flight not found with this id")
    
#     try:
#         db.delete(flight)
#         db.commit()
#         return None
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="Database error occurr")