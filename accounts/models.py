from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings



# ─────────────── USER ─────────────── #
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('lab', 'Lab Staff'),   # ✅ New user type
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='patient')

    @property
    def is_patient(self):
        return self.user_type == 'patient'

    @property
    def is_doctor(self):
        return self.user_type == 'doctor'
    
    @property
    def is_lab(self):
        return self.user_type == 'lab'




# ─────────────── DOCTOR PROFILE ─────────────── #
class DoctorProfile(models.Model):
    SPECIALIZATION_CHOICES = [
    ('Cardiologist', 'Cardiologist'),
    ('Dermatologist', 'Dermatologist'),
    ('Neurologist', 'Neurologist'),
    ('Pediatrician', 'Pediatrician'),
    ('Orthopedic', 'Orthopedic'),
    ('Gynecologist', 'Gynecologist'),
    ('General Physician', 'General Physician'),
    ('ENT Specialist', 'ENT Specialist'),
]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, choices=SPECIALIZATION_CHOICES)
    hospital = models.CharField(max_length=100)
    experience = models.PositiveIntegerField()
    profile_picture = models.ImageField(upload_to='doctor_profile_pictures/', blank=True, null=True, default='default.jpg')
    meeting_link = models.URLField(blank=True, null=True)
    qualification = models.CharField(max_length=200, default="MBBS")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.specialization}"
# ─────────────── PATIENT PROFILE ─────────────── #
class PatientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

# ─────────────── TIME SLOT ─────────────── #
class TimeSlot(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.date} {self.start_time}-{self.end_time}"


# ─────────────── LOGIN LOG ─────────────── #
class LoginLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='login_logs')
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'login_log'
        ordering = ['-login_time']



class LabProfile(models.Model):
    LAB_CHOICES = [
        ('city lab', 'city lab'),
        ('shifa diagnostics', 'shifa diagnostics'),
        ('excel lab', 'excel lab'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lab_name = models.CharField(max_length=100, choices=LAB_CHOICES)

    def __str__(self):
        return f"{self.lab_name} ({self.user.username})"