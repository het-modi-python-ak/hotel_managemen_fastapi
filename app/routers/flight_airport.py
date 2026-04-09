from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.database import get_db
from app.models.flight_models import Airport 
from app.schemas.schemas import AirportCreate,AirporResponse
from app.core.dependencies import get_current_user
from app.schemas.schemas import AirportUpdate 

router = APIRouter()


@router.post("/") 
def create_airport(airport: AirportCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        existing_airport = db.query(Airport).filter(Airport.code == airport.code).first()
        if existing_airport:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Airport with this code already exists")
        
        new_airport = Airport(code=airport.code, name=airport.name, location=airport.location, country=airport.country)
        
        db.add(new_airport)
        db.commit()
        db.refresh(new_airport)
        
       
        return new_airport
        
    except SQLAlchemyError as e:
        db.rollback()
        
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")




from typing import List


# GET: Retrieve all airports
@router.get("/", response_model=List[AirporResponse])
def get_airports(db: Session = Depends(get_db)):
    return db.query(Airport).all()

# GET: Retrieve a single airport by its code
@router.get("/{airport_code}")
def get_airport(airport_code: str, db: Session = Depends(get_db)):
    airport = db.query(Airport).filter(Airport.code == airport_code).first()
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    return airport

# UPDATE: Modify an existing airport record
@router.patch("/{airport_code}")
def update_airport(airport_code: str, airport_data: AirportUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_airport = db.query(Airport).filter(Airport.code == airport_code).first()
    if not db_airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    # Update fields
    if (airport_data.name):
          db_airport.name = airport_data.name
   
    
    
    try:
        db.commit()
        db.refresh(db_airport)
        return db_airport
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error during update")

# DELETE: Remove an airport record
@router.delete("/{airport_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_airport(airport_code: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_airport = db.query(Airport).filter(Airport.code == airport_code).first()
    if not db_airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    try:
        db.delete(db_airport)
        db.commit()
        return None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error during deletion")
