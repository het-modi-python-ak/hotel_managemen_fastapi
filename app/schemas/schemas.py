from pydantic import BaseModel
from typing import Optional

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
