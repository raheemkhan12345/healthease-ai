from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.conf import settings
import os
from django.utils import timezone

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='patient')
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=True)

    
    

class DoctorProfile(models.Model): 
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,     # Automatically uses 'accounts.User'
        on_delete=models.CASCADE,
        primary_key=True
    )
    specialization = models.CharField(max_length=100)
    hospital = models.CharField(max_length=100)
    experience = models.IntegerField()
    profile_picture = models.ImageField(
        upload_to='doctor_profile_pictures/',
        default='default.jpg',
        blank=True, null=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.specialization}"

class PatientProfile(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    # Removed duplicate username field (already in User model)

    def __str__(self):
        return f"{self.user.username}'s Patient Profile"

class LoginLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='login_logs'
    )
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        db_table = 'login_log'
        ordering = ['-login_time']