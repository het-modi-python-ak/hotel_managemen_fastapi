from app.core.celery_app import celery_app
from app.services.email_service import send_reminder_email


@celery_app.task
def send_booking_reminder(email:str,booking_id:int):
    send_reminder_email(email,booking_id)