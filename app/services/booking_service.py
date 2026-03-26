from sqlalchemy.orm import Session
from sqlalchemy import func
from models.booking_item import BookingItem
from models.room import Room

def get_available_rooms(db: Session, hotel_id, room_type, check_in, check_out):
    # 1. Total rooms of this type in the hotel
    total_rooms_query = db.query(func.sum(Room.total_rooms)).filter(
        Room.hotel_id == hotel_id,
        Room.room_type == room_type
    ).scalar() or 0

    # 2. Total rooms already booked for this type in date range
    booked_rooms_query = db.query(func.sum(BookingItem.quantity)).join(
        Room, BookingItem.room_id == Room.room_id
    ).filter(
        Room.hotel_id == hotel_id,
        Room.room_type == room_type,
        BookingItem.check_out > check_in,
        BookingItem.check_in < check_out
    ).scalar() or 0

    return total_rooms_query - booked_rooms_query
