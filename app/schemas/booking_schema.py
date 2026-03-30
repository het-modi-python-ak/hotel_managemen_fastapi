from pydantic import BaseModel
from datetime import date
from models.room_type import RoomType


class BookingItemCreate(BaseModel):

    room_type: RoomType
    quantity: int


class BookingCreate(BaseModel):

    hotel_id: int
    check_in: date
    check_out: date
    no_of_people: int
    rooms: list[BookingItemCreate]
