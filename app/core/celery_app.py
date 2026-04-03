from celery import Celery

celery_app = Celery("hotel_booking", broker="redis://localhost:6379/0",backend="redis://localhost:6379/0" , include=["app.tasks.reminder_tasks"] )
celery_app.conf.task_routes={"app.tasks.remider_tasks.*":{"queue":"emails"}}