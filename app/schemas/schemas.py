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
    
    
# class FlightBooking(BaseModel):
#     flight_id:int
    
    
    
    
    
#seat 

class SeatCreate(BaseModel):
    business:int =0
    economy:int=0
    premium:int=0
    
    
