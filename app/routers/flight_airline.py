from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.database import get_db
from app.models.flight_models import Airline
from app.core.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()

class CreateArline(BaseModel):
    name:str
    country:str

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_airline(
    # name: str,
    # country: str,
    data : CreateArline,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        name = data.name
        country = data.country
        existing_airline = db.query(Airline).filter(Airline.name == name).first()
        if existing_airline:
            raise HTTPException(status_code=400, detail="Airline already exists")

        airline = Airline(name=name, country=country, created_by=current_user.id )
        db.add(airline)
        db.commit()
        db.refresh(airline)
        return airline
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while creating airline")



@router.get("/")
def get_all_airlines(db: Session = Depends(get_db)):
    try:
        airlines = db.query(Airline).all()
        if not airlines:
            raise HTTPException(status_code=404, detail="No airlines found")
        return airlines
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error fetching airlines from database")



@router.get("/my")
def get_all_airlines(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        airlines = db.query(Airline).filter(Airline.created_by==current_user.id).all()
        if not airlines:
            raise HTTPException(status_code=404, detail="No airlines found")
        return airlines
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error fetching airlines from database")




@router.get("/{airline_id}")
def get_airline(airline_id: int, db: Session = Depends(get_db)):
    try:
        airline = db.query(Airline).filter(Airline.airline_id == airline_id).first()
        if not airline:
            raise HTTPException(status_code=404, detail="Airline not found")
        return airline
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error fetching airline details")


class UpdateArline(BaseModel):
    airline_id:int
    name:str | None = None
    country: str | None = None

@router.patch("/{airline_id}")
def update_airline(
    # airline_id: int,
    # name: str | None = None,
    # country: str | None = None,
    data : UpdateArline,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        airline_id = data.airline_id
        name = data.name
        country = data.country
        
        airline = db.query(Airline).filter(Airline.airline_id == airline_id,Airline.created_by==current_user.id).first()
        if not airline:
            raise HTTPException(status_code=404, detail="Airline not found")

        if name:
            duplicate = db.query(Airline).filter(Airline.name == name, Airline.airline_id != airline_id).first()
            if duplicate:
                raise HTTPException(status_code=400, detail="Airline with this name already exists")
            airline.name = name
        
        if country:
            airline.country = country

        db.commit()
        db.refresh(airline)
        return airline
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating airline")



@router.delete("/{airline_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_airline(airline_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        airline = db.query(Airline).filter(Airline.airline_id == airline_id,Airline.created_by==current_user.id).first()
        if not airline:
            raise HTTPException(status_code=404, detail="Airline not found")

        db.delete(airline)
        db.commit()
        return None 
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting airline")
