from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import DoctorProfile, PatientProfile, TimeSlot
from datetime import datetime, timedelta


User = get_user_model()  # This ensures the correct User model is used

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
    reason = models.TextField(blank=True, null=True)
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


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient.username}"

class LabTest(models.Model):
    LAB_CHOICES = [
        ('City Lab', 'City Lab'),
        ('Shifa Diagnostics', 'Shifa Diagnostics'),
        ('Excel Lab', 'Excel Lab'),
    ]

    test_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    lab_name = models.CharField(max_length=255, choices=LAB_CHOICES, blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=[('Pending', 'Pending'), ('Completed', 'Completed')],
        default='Pending'
    )
    report_file = models.FileField(upload_to='lab_reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.test_name} for {self.patient.user.username}"