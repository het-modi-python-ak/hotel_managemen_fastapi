
from sqlalchemy.orm import Session
from models.booking_item import BookingItem
from models.room import Room


def get_available_rooms(db: Session, room_id, check_in, check_out):

    room = db.query(Room).filter(Room.room_id == room_id).first()

    bookings = db.query(BookingItem).filter(
        BookingItem.room_id == room_id,
        BookingItem.check_out > check_in,
        BookingItem.check_in < check_out
    ).all()

    booked = sum(b.quantity for b in bookings)

    return room.total_rooms - booked