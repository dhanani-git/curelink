#!/usr/bin/env python3
import os
import sys
import django

# Add project to path
sys.path.insert(0, '/home/nakul/Development/CureLink')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctors_app.settings')
django.setup()

from Hospitals.models import Appointment

apt = Appointment.objects.first()
if apt:
    print(f"✅ Found appointment:")
    print(f"   User: {apt.user.email}")
    print(f"   Date/Time: {apt.appointment_date} {apt.time}")
    print(f"   Reminder sent: {apt.reminder_sent}")
    
    apt.reminder_sent = False
    apt.reminder_sent_at = None
    apt.save()
    
    print(f"\n✅ Reset complete! Reminder flag = {apt.reminder_sent}")
else:
    print("❌ No appointments found!")
