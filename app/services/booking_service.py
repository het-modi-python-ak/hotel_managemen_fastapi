from sqlalchemy import func
from models.booking import Booking
# return the rooms which are booked 

def get_booked_rooms(db,room_id,check_in,check_out):
    booked = db.query(func.sum(Booking.total_room)).filer(Booking.room_id==room_id,Booking.status != "cancelled", Booking.check_in<Booking.check_out).scalar()
    return booked or 0
