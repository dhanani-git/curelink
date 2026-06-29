from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import transaction
from .models import State, Hospital, Doctor, Timing, Review, Appointment, doctor_departments
from datetime import datetime, date
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import json
from django.core import serializers

# Helper function: Check if user is authenticated
def is_authenticated(user):
    return user.is_authenticated

# Helper function: Check if user is admin
def is_admin(user):
    return user.is_staff

# Helper function: Get coordinates from location string
def get_location_coordinates(location):
    try:
        geolocator = Nominatim(user_agent="doctors_app")
        location_data = geolocator.geocode(location)
        if location_data:
            return (location_data.latitude, location_data.longitude)
    except:
        pass
    return None
# Create your views here.

@user_passes_test(is_authenticated, login_url='/login/')
def home_page(request):
    states = State.objects.all()
    selected_state = request.GET.get('state', '')
    if selected_state:
        hospitals = Hospital.objects.filter(state_id=selected_state)
    else:
        hospitals = Hospital.objects.all()
    
    paginator = Paginator(hospitals, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    list_range = [1, 2, 3, 4, 5]

    nearest_hospitals = []
    if request.method == 'POST':
        user_latitude = request.POST.get('latitude')
        user_longitude = request.POST.get('longitude')
        
        if user_longitude and user_latitude:
            user_location = (float(user_latitude), float(user_longitude))
            all_hospitals = Hospital.objects.all()
            hospital_distances = []
            for hospital in all_hospitals:
                if hospital.location:
                    hospital_coords = get_location_coordinates(hospital.location)
                    if hospital_coords:
                        distance = geodesic(user_location, hospital_coords).kilometers
                        hospital_distances.append((hospital, distance))
            hospital_distances.sort(key=lambda x: x[1])
            nearest_hospitals = hospital_distances[:3]

    recommended_doctors = []
    user_appointments = Appointment.objects.filter(user=request.user)
    if user_appointments.exists():
        doctor_ids = user_appointments.values_list('doctor_id', flat=True).distinct()
        recommended_doctors = Doctor.objects.filter(id__in=doctor_ids)[:3]
    context = {
        'hospitals': page_obj,
        'states': states,
        'list': list_range,
        'nearest_hospitals': nearest_hospitals,
        'doctors': recommended_doctors,
    }
    return render(request, 'Hospital/home.html', context)

@transaction.atomic
@user_passes_test(is_admin, login_url='/login/')
def add_doctor(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        mobile = request.POST['mobile']
        department = request.POST['department']
        qualifications = request.POST.get('qualifications', 'MBBS')
        profile_pic = request.FILES.get('profile_pic')
        hospital_ids = request.POST.getlist('hospitals')
    
        doctor = Doctor.objects.create(
            first_name = first_name,
            last_name = last_name,
            mobile = mobile,
            department = department,
            qualifications = qualifications,
            profile_pic = profile_pic,
        )
        doctor.hospitals.set(hospital_ids)

        messages.success(request, 'Doctor added successfully')
        return redirect('/')

    context = {'hospital_ch': Hospital.objects.all(), 'depts': doctor_departments,}
    return render(request, 'Hospital/add_doctor.html', context)

@user_passes_test(is_authenticated, login_url='/login/')
def view_doctors(request):
    department = request.GET.get('department', '')
    if department:
        doctors = Doctor.objects.filter(department=department)
    else:
        doctors = Doctor.objects.all()
    
    context = {
        'doctors': doctors,
        'depts': doctor_departments,
    }
    return render(request, 'Hospital/view_doctors.html', context)

@user_passes_test(is_authenticated, login_url='/login/')
def view_all_doctors(request, hospital_id):
    hospital = Hospital.objects.get(id=hospital_id)
    doctors = hospital.doctors.all()
    timings = Timing.objects.filter(hospital=hospital)
    context = {'hospital': hospital, 'doctors': doctors, 'timings': timings}
    return render(request, 'Hospital/view_all_doctors.html', context)
    
@user_passes_test(is_authenticated, login_url='/login/')
def doctor_profile(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)
    reviews = Review.objects.filter(doctor=doctor).order_by('-rating')[:5]
    if request.method == 'POST' and request.user.is_staff:
        review_id = request.POST.get('review_id_to_delete')
        if review_id:
            Review.objects.filter(id=review_id).delete()
            messages.success(request, 'Review deleted successfully')
            return redirect('doctor_profile', doctor_id=doctor_id)
    context = {'doctor':doctor, 'top_reviews':reviews, 'hospitals':doctor.hospitals.all(),
    'list': [1,2,3,4,5]}
    return render(request, 'Hospital/doctor_profile.html', context)

@user_passes_test(is_authenticated, login_url='/login/')
def add_review(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)
    if request.method == 'POST':
        rating = request.POST['rating']
        comment = request.POST.get('comment', '')

        Review.objects.create(
            user = request.user,
            doctor = doctor,
            rating = rating,
            comment = comment
        )

        messages.success(request, 'Review added successfully')
        return redirect('doctor_profile', doctor_id=doctor_id)
    
    context = {'doctor': doctor}
    return render(request, 'Hospital/add_review.html', context)

@user_passes_test(is_authenticated, login_url='/login/')
def doctor_appointments(request, doctor_id, hospital_id):
    doctor = Doctor.objects.get(id=doctor_id)
    hospital = Hospital.objects.get(id=hospital_id)
    if request.method == 'POST':
        appointment_date = request.POST['appointment_date']
        time = request.POST['time']
        notes = request.POST.get('notes', '')

        Appointment.objects.create(
            user = request.user,
            doctor = doctor,
            hospital = hospital,
            appointment_date = appointment_date,
            time = time,
            notes = notes
        )
        messages.success(request, 'Appointment added successfully')
        return redirect('user_dashboard')
    
    context = {'doctor': doctor, 'hospital': hospital}
    return render(request, 'Hospital/book_appointment.html', context)

def get_available_timings(request):
    if request.method == 'GET':
        doctor_id = request.GET.get('doctor_id')
        hospital_id = request.GET.get('hospital_id')
        date_str = request.GET.get('date_str')
        
        if doctor_id and hospital_id and date_str:
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            day_of_week = appointment_date.strftime('%A')
            timings = Timing.objects.filter(
                doctor_id=doctor_id,
                hospital_id=hospital_id,
                day_of_week=day_of_week
            )

            available_timings = []
            for timing in timings:
                booked = Appointment.objects.filter(
                    doctor_id=doctor_id,
                    hospital_id=hospital_id,
                    appointment_date=appointment_date,
                    time=timing.start_time).exists()

                if not booked:
                    available_timings.append({
                        'time': timing.start_time.strftime('%H:%M'),
                        'display': f"{timing.start_time.strftime('%I:%M %p')} - {timing.end_time.strftime('%I:%M %p')}"
                    })

            return JsonResponse({'available_timings': available_timings},
            safe=False)
            
    return JsonResponse([], safe=False)

@user_passes_test(is_authenticated, login_url='/login/')
def dashboard(request):
    upcoming_appointments = Appointment.objects.filter(user=request.user, status=True,
    appointment_date__gte=date.today()).order_by('appointment_date', 'time')
    
    past_appointments = Appointment.objects.filter(user=request.user,
    status=False).order_by('-appointment_date', 'time')
    context = {'upcoming_appointments': upcoming_appointments,
    'past_appointments': past_appointments}
    return render(request, 'Hospital/dashboard.html', context)

@user_passes_test(is_authenticated, login_url='/login/')
def cancel_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id, user = request.user)
    appointment.status = False
    appointment.save()
    messages.success(request, 'Appointment cancelled successfully')
    return redirect('user_dashboard')

@user_passes_test(is_authenticated, login_url='/login/')
def reschedule_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id,
    user=request.user)
    if request.method == 'POST':
        new_date = request.POST['appointment_date']
        new_time = request.POST['time']
        appointment.appointment_date = new_date
        appointment.time = new_time
        appointment.save()
        messages.success(request, 'Appointment rescheduled successfully')
        return redirect('user_dashboard')
    

    context = {'appointment': appointment,}
    return render(request, 'Hospital/reschedule_appointment.html', context)

@user_passes_test(is_authenticated, login_url='/login/')
def  create_prescription(request, appointment_id):
    