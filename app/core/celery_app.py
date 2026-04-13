from celery import Celery

# celery_app = Celery("hotel_booking", broker="redis://localhost:6379/0",backend="redis://localhost:6379/0" , include=["app.tasks.reminder_tasks"] )
# celery_app.conf.task_routes={"app.tasks.remider_tasks.*":{"queue":"emails"}}


# celery = Celery("hotel_booking", broker="redis://localhost:6379/0",backend="redis://localhost:6379/0" )
# Celery.conf.beat_schedule = {"check-flight-reminders-every-minute":{"task":"app.tasks.reminder_task.check_flight_reminders","schedule":60.0}}
# celery.conf.timezone="UTC"
# from celery import Celery

# Initialize the app instance
celery = Celery('hotel_booking', "flight_tasks",
             broker='redis://localhost:6379/0', 
             backend='redis://localhost:6379/0')

# Use the 'app' instance, not the 'Celery' class
celery.conf.beat_schedule = {
    'check-flight-reminders-every-minute': {
        'task': 'app.tasks.reminder_task.check_flight_reminders',
        'schedule': 60.0,
    },
}

celery.conf.timezone = 'UTC'