from pydantic import BaseModel
from typing import Optional
from datetime import date
from typing import List
from models.room_type import RoomType



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

    