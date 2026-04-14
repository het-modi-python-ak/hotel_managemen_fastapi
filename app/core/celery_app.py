from celery import Celery

# celery_app = Celery("hotel_booking", broker="redis://localhost:6379/0",backend="redis://localhost:6379/0" , include=["celery.tasks.reminder_tasks"] )
# celery_app.conf.task_routes={"celery.tasks.remider_tasks.*":{"queue":"emails"}}


# celery = Celery("hotel_booking", broker="redis://localhost:6379/0",backend="redis://localhost:6379/0" )
# Celery.conf.beat_schedule = {"check-flight-reminders-every-minute":{"task":"celery.tasks.reminder_task.check_flight_reminders","schedule":60.0}}
# celery.conf.timezone="UTC"
# from celery import Celery

# Initialize the celery instance
# celery = Celery('hotel_booking', "flight_tasks",
#              broker='redis://localhost:6379/0', 
#              backend='redis://localhost:6379/0')

# # Use the 'celery' instance, not the 'Celery' class
# celery.conf.beat_schedule = {
#     'check-flight-reminders-every-minute': {
#         'task': 'celery.tasks.reminder_task.check_flight_reminders',
#         'schedule': 60.0,
#     },
# }

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
