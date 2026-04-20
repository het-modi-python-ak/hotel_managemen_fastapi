from celery import Celery


# celery.conf.timezone = 'UTC'

from celery import Celery
# from app.tasks.reminder_tasks import check_flight_reminders

# Create the celery 
celery = Celery(
    'hotel_booking',
    broker='redis://localhost:6379/0',
    # backend='redis://localhost:6379/0',
    include=['app.tasks.reminder_tasks']  #
)

#  Celery Beat
celery.conf.beat_schedule = {
    'check-flight-reminders-every-minute': {
        'task': 'app.tasks.reminder_tasks.check_flight_reminders',
        'schedule': 60.0,
    },
}

celery.conf.timezone = 'UTC'
