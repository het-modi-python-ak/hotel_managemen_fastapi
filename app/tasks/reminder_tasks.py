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



from app.core.celery_app import celery_app
from app.services.email_service import send_reminder_email


@celery_app.task
def send_booking_reminder(email:str,booking_id:int):
    send_reminder_email(email,booking_id)