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
    
    
    
    
async def send_verification_email(email:str,token:str):
    verify_link = f"http://localhost:8000/auth/verify-email?token={token}"
    
    message = MessageSchema(subject="Verify your email", recipients=[email],body=f"click the link to  verify your email \n {verify_link}",subtype="plain" )
    fm = FastMail(conf)
    await fm.send_message(message)
    
    
    
    
    
import asyncio    


def send_reminder_email_flight(email:str,flight_id:int):
    message=MessageSchema(subject="Take off reminder", recipients=[email],body=f"the flight with number {flight_id} is going to takeoff in  few minutes ",subtype="plain")
    fm = FastMail(conf)
    print("sending the email")
    asyncio.run(fm.send_message(message))



def send_reminder_email(email:str,booking_id:int):
    async def _send():
        message=MessageSchema(subject="Booking reminder", recipients=[email],body=f"please confirm your booking (ID) : {booking_id} before it expires", subtype="plain")
        fm = FastMail(conf)
        await fm.send_message(message)
    
    asyncio.run(_send())

