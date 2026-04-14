# from app.core.celery_app import celery_app
# from app.services.email_service import send_reminder_email
# from app.database.database import SessionLocal
# from app.models.booking import Booking

# @celery_app.task
# def send_booking_reminder(email:str,booking_id:int):
    
#     db = SessionLocal()
    
#     booking = db.query(Booking).filter(Booking.booking_id==booking_id).first()
    
#     if booking :
#         send_reminder_email(email,booking_id)
#     db.close()



from app.core.celery_app import celery
from app.services.email_service import send_reminder_email
from sqlalchemy.orm import Session
from app.core.celery_app import celery
from app.database.database import SessionLocal
from app.models.flight_models import FlightBooking
from app.models.flight_models import Flight
from app.services.notification_service import send_notification
from datetime import datetime,timedelta
from app.models.user_email import User2

@celery.task
def send_booking_reminder(email:str,booking_id:int):
    send_reminder_email(email,booking_id)
    
@celery.task   
def check_flight_reminders():
    print("checking flight reminders ... ")
    db:Session = SessionLocal()
    now = datetime.now()
    target  = not + timedelta(minutes=10)
    bookings = (db.query(FlightBooking)).join(Flight).filter(Flight.depart_time>=now,Flight.depart_time<=target,FlightBooking.reminder_sent==False).all()
    user = db.query(User2).filter(User2.id==booking.created_by).first()
    
    
    for booking in bookings:
        send_notification(user.email,booking.flight.flight_number) 
        booking.reminder_sent=True
        db.commit()
        db.close()
    
    
    