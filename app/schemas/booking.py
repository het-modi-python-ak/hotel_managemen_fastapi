from pydantic import BaseModel,model_validator
from datetime import date

class BookingItemCreate(BaseModel):
    room_type:str
    quantity:int

class BookingCreate(BaseModel):
    hotel_id:int
    check_in:date
    check_out:date
    no_of_people:int
    rooms:list[BookingItemCreate]


@model_validator(mode="after")
def validate_dates(self):

    if self.cehck_out<=self.check_in:
        raise ValueError("check_out must be after chek_in")
    return self


