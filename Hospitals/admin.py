from django.contrib import admin
from .models import State, Hospital, Doctor, Timing, Review, Appointment

admin.site.register(State)
admin.site.register(Hospital)
admin.site.register(Doctor)
admin.site.register(Timing)
admin.site.register(Review)
admin.site.register(Appointment)