from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Appointment
from datetime import datetime, timedelta
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_appointment_reminders():
    now = timezone.now()
    reminder_time = now + timedelta(hours=5)
    start_time = reminder_time - timedelta(minutes=30)  # 30 min before
    end_time = reminder_time + timedelta(minutes=30)     # 30 min after

    # Get all active appointments (don't filter by date to handle midnight crossings)
    appointments = Appointment.objects.filter(
        status=True,
        reminder_sent=False
    ).select_related('user', 'doctor', 'hospital')

    appointments_to_remind = []
    for apt in appointments:
        apt_time = timezone.make_aware(datetime.combine(
            apt.appointment_date, apt.time
        ))

        if(start_time <= apt_time <= end_time):
            appointments_to_remind.append(apt)

    count=0
    for apt in appointments_to_remind:
        try:
            send_reminder_email.delay(apt.id)
            apt.reminder_sent = True
            apt.reminder_sent_at = timezone.now()
            apt.save()
            count+=1
        except Exception as e:
            logger.error(f"Failed to queue reminder for appointment {apt.id}: {e}")
    logger.info(f"Queued {count} appointment reminders")
    return f"Queued {count} reminders"

@shared_task
def send_reminder_email(appointment_id):

    try:
        appointment = Appointment.objects.select_related('user', 'doctor', 'hospital').get(id=appointment_id)
        html_message = render_to_string('emails/appointment_reminder.html', {
            'user': appointment.user,
            'appointment': appointment
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f'Appointment Reminder - CureLink',
            message=plain_message,
            from_email=None,
            recipient_list=[appointment.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Sent reminder to {appointment.user.email} for appointment ID {appointment.id}")
        return f"Sent reminder to {appointment.user.email}"

    except Appointment.DoesNotExist:
        logger.error(f"Appointment {appointment_id} not found")
        return f"Appointment {appointment_id} not found"

    except Exception as e:
        logger.error(f"Failed to send reminder for appointment {appointment_id}: {e}")
        raise