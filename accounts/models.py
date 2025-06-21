# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

class User(AbstractUser):
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)
    
class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    specialization = models.CharField(max_length=100)
    hospital = models.CharField(max_length=100)
    experience = models.IntegerField(default=0)  # Simple integer field
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    class Meta:
        # Add this if your table name has a typo
        db_table = 'accounts_doctorprofile' 
        
    def __str__(self):
        return f"{self.user.username}'s Profile"

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    date_of_birth = models.DateField()

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    
    User = get_user_model()

class LoginLog(models.Model):
    """Tracks user login/logout activity"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_logs')
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    session_key = models.CharField(max_length=40)
    
    class Meta:
        db_table = 'login_log'  # Matches your existing table
        ordering = ['-login_time']
        
    def __str__(self):
        return f"{self.user.username} logged in at {self.login_time}"