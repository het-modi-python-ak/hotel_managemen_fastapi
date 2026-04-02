from fastapi_mail import FastMail,MessageSchema
from app.core.email_config import conf


async def send_booking_confirmation_email(email:str,booking_id:int):
    message = MessageSchema(
        subject = "Booking confirmed",
        recipients=[email],
        body=f"YOur booking with ID {booking_id} has been confirmed successfully",
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    
    
async def send_cancellation_email(email:str,booking_id:int):
    message = MessageSchema(
        subject="Booking cancelled",
        recipients=[email],
        body=f"Your booking with ID {booking_id} has been cancelled",
        subtype="plain"
        
    )
    fm = FastMail(conf)
    await fm.send_message(message)