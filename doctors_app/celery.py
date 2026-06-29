import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 
'doctors_app.settings')

app = Celery('doctors_app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-appointment-reminders-every-hour': {
        'task': 'Hospitals.tasks.send_appointment_reminders',
        'schedule': crontab(minute=32),  # Will run at 11:32 PM
    },
}
