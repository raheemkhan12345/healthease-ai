# chat/models.py
from django.db import models
from accounts.models import User

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    hospital = models.CharField(max_length=100)
    patients = models.ManyToManyField(User, related_name='doctors', blank=True)
    
    def __str__(self):
        return f"Dr. {self.user.username}"

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=5)
    allergies = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}"

class Appointment(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=(
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ), default='Pending')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Appointment {self.id} - Dr. {self.doctor.username} with {self.patient.username}"