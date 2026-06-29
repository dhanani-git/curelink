from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.core.exceptions import ValidationError
from datetime import date

doctor_departments = [
  "Cardiology",
  "Orthopedics",
  "Dermatology",
  "Pediatrics",
  "Obstetrics and Gynecology",
  "Neurology",
  "Ophthalmology",
  "ENT (Ear, Nose, and Throat)"
]

department_choices = [(d, d) for d in doctor_departments]
class State(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Hospital(models.Model):
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    name  = models.CharField(max_length=100)
    address = models.TextField()
    contact_no = models.CharField(max_length=15)
    description = models.TextField(default="A leading healthcare institution committed to providing high-quality medical care and compassionate services to our patients.")
    image = models.ImageField(upload_to='hospital_images/', null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

    # Property to get image URL or default placeholder
    def get_url(self):
        if self.image:
            return self.image.url
        return "https://via.placeholder.com/150"

    @property
    def average_doctor_rating(self):
        doctors = self.doctors.all()
        if doctors:
            avg = doctors.aggregate(Avg('reviews__rating'))['reviews__rating__avg']
            return round(avg, 1) if avg else 0
        return 0
    
class Doctor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_pic = models.ImageField(upload_to='doctor_images/', 
    null=True, blank=True)
    mobile = models.CharField(max_length=15)
    department = models.CharField(max_length=100, choices=department_choices)
    qualifications = models.TextField(default = "MBBS")
    status = models.BooleanField(default=True)
    hospitals = models.ManyToManyField(Hospital, related_name="doctors")

    def __str__(self):
        return f"Dr.{self.first_name} {self.last_name}"
        
    def get_name(self):
        return f"Dr.{self.first_name} {self.last_name}"

class Timing(models.Model):
    DAY_CHOICES = [('Monday', 'Monday'), ('Tuesday', 'Tuesday'), 
    ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), 
    ('Friday', 'Friday'), ('Saturday', 'Saturday'), 
    ('Sunday', 'Sunday')]
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def __str__(self):
        return f"{self.doctor} - {self.hospital.name} {self.day_of_week} {self.start_time} - {self.end_time}"

def validate_rating(value):
    if value>5 or value<0:
        raise ValidationError("Rating must be between 0 and 5")

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, 
    related_name="reviews")
    rating = models.BigIntegerField(default=0, 
    validators=[validate_rating])
    comment = models.TextField(null = True, blank = True)

    def __str__(self):
        return f"{self.user.username} - {self.doctor.get_name()} - {self.rating} stars"
    
class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank = True)
    status = models.BooleanField(default=True)
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.doctor.get_name()} on {self.appointment_date} {self.time}"
    
    # def save(self, *args, **kwargs):
    #     if self.appointment_date < date.today():
    #         self.status = False
    #     super(Appointment, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(Appointment, self).save(*args, **kwargs)

class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    
    diagnosis = models.TextField()
    medicines = models.TextField(help_text="List of medicines with dosage")
    instructions = models.TextField(blank=True)
    tests = models.TextField(blank=True, help_text="Recommended tests")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Prescription for {self.patient.username} by Dr. {self.doctor.get_name()}"
    
    class Meta:
        ordering = ['-created_at']
