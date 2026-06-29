from django.urls import path
from . import views
urlpatterns = [
    path('', views.home_page, name='home'),
    path('doctors/', views.add_doctor, name='doctors'),
    path('view-doctors/', views.view_doctors, name='view_doctors'),
    path('view-all-doctors/<int:hospital_id>/', views.view_all_doctors, name='view_all_doctors'),
    path('doctor-profile/<int:doctor_id>/', views.doctor_profile, name='doctor_profile'),
    path('book-appointment/<int:doctor_id>/<int:hospital_id>/', views.doctor_appointments, name='doctor_appointment'),
    path('dashboard/', views.dashboard, name='user_dashboard'),
    path('add-review/<int:doctor_id>/', views.add_review, name='add_review'),
    path('cancel-appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('reschedule-appointment/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('get_available_timings/', views.get_available_timings, name='get_available_timings'),
]
