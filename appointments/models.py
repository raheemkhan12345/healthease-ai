from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils.translation import gettext_lazy as _
from accounts.models import User, DoctorProfile, PatientProfile
from django.core.validators import MinValueValidator
from datetime import datetime, timedelta
from accounts.models import TimeSlot



class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='healthease_user_set',
        related_query_name='healthease_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='healthease_user_set',
        related_query_name='healthease_user',
    )

    class Meta:
        db_table = 'healthease_user'


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    zoom_meeting_id = models.CharField(max_length=100, blank=True, null=True)
    zoom_join_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.patient.user.username} with Dr. {self.doctor.user.username} on {self.date} at {self.start_time}"

    def save(self, *args, **kwargs):
        if not self.end_time:
            self.end_time = (datetime.combine(datetime.today(), self.start_time) + timedelta(minutes=30)).time()
        super().save(*args, **kwargs)