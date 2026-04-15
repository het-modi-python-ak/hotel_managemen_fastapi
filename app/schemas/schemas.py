from pydantic import BaseModel, Field
from typing import Optional
from datetime import date,datetime
from typing import List
from app.models.room_type import RoomType



class HotelResponse(BaseModel):

    id: int
    owner_id: int
    name: str
    address: str
    city: str
    state: str
    country: str
    rating: Optional[float]

    class Config:
     
        from_attributes = True 



class CreateHotel(BaseModel):
    name: str
    address: str
    city: str
    state: str
    country: str
    
class RoomRequest(BaseModel):
    room_type: RoomType
    quantity: int


class BookingRequest(BaseModel):
    hotel_id: int
    check_in: date
    check_out: date
    rooms: List[RoomRequest]


class BookingItemResponse(BaseModel):
    room_id:int
    quantity:int
    check_in:date
    check_out:date

    

# #airport
# class AirportCreate(BaseModel):
#     code:str
#     name:str
#     location:str
#     country:str
    
    

# class AirporResponse(BaseModel):
#     id :int
#     code:str
#     name:str
#     location:str
#     country:str
    
    
# class AirportUpdate(BaseModel):
#     name:str
    
# #flight 
# class FlightCreate(BaseModel):
#     flight_number:str
#     source_id:int
#     destination_id:int
#     depart_time:datetime
#     arrival_time:datetime
    
    
    
    
# class FlightResponse(BaseModel):
#     flight_id:int
#     flight_number:str
#     source_id:int
#     destination_id:int
#     depart_time:datetime
#     arrival_time:datetime
    
    
# class FlightUpdate(BaseModel):
#     depart_time:datetime
#     arrival_time:datetime
    
    
    

# #seat 

# class SeatBase(BaseModel):
#     flight_id: int
#     seat_number: str = Field(..., max_length=50, example="12A")
#     seat_class: str = Field(..., max_length=50, example="Economy")
#     is_booked: bool = False
#     price: int = Field(..., gt=0, description="Price must be greater than zero")

# # Schema for incoming POST requests
# class SeatCreate(SeatBase):
#     pass

# # Schema for the API response
# class SeatResponse(SeatBase):
#     seat_id: int




# class FlightData(BaseModel):
#     seat_id:int
    
    
class FlightBookingreposnse(BaseModel):
    booking_id:int
    flight_id:int
    seat_number:str
    status:str
    total_price:int
    created_by:int
    
    
    
    
    
    
#seat 

class SeatCreate(BaseModel):
    business:int =0
    economy:int=0
    premium:int=0
    
    
    
class CreateArline(BaseModel):
    name:str
    country:str



from enum import Enum

class SeatCategory(str, Enum):
    BUSINESS = "BUSINESS"
    ECONOMY = "ECONOMY"
    PREMIUM = "PREMIUM"
    
    
    
class CreateAirplane(BaseModel):
    model: str
    total_seats: int
    airline_id: int
    total_business_seat: int
    total_economy_seat: int
    total_premium_seat: int



class CreateAirport(BaseModel):
    code:str
    name:str
    location:str
    country:str



class Bookseats(BaseModel):
    flight_id:int
    seat_numbers:List[str]
    
    
    
class CreateFlight(BaseModel):
    flight_number: str
    airplane_id: int
    source_id: int
    destination_id: int
    depart_time: datetime
    arrival_time: datetime
    
    
from app.core.hotel_enums import StateEnum, CountryEnum
class HotelUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[StateEnum] = None
    country: Optional[CountryEnum] = None
