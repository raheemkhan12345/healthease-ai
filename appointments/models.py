from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import DoctorProfile, PatientProfile, TimeSlot
from datetime import datetime, timedelta, timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import make_aware, now

User = get_user_model()  

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    prescription = models.FileField(upload_to='prescriptions/', blank=True, null=True)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    transaction_id = models.CharField(max_length=11, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def jitsi_room_name(self):
        return f"consult_{self.id}_{self.doctor.user.username}_{self.patient.user.username}".replace(" ", "_")


    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.patient.user.username} with Dr. {self.doctor.user.username} on {self.date} at {self.start_time}"

    def save(self, *args, **kwargs):
        if not self.end_time:
            self.end_time = (datetime.combine(datetime.today(), self.start_time) + timedelta(minutes=30)).time()
        super().save(*args, **kwargs)
        
    def get_start_datetime(self):
        from datetime import datetime
        return make_aware(datetime.combine(self.date, self.start_time))
    def can_join_consultation(self):
        """Check if patient/doctor can join consultation window."""
        start_dt = self.get_start_datetime()
        join_window_start = start_dt - timedelta(minutes=15)   # 15 min before
        join_window_end = start_dt + timedelta(minutes=45)     # 30 min consult + 15 after
        return join_window_start <= now() <= join_window_end


class LabTest(models.Model):
    STATUS_CHOICES = [
        ('Suggested', 'Suggested by Doctor'),         
        ('Details Pending', 'Patient Details Needed'), 
        ('Sent to Lab', 'Sent to Laboratory'),        
        ('Sample Collected', 'Sample Collected'),     
        ('In Progress', 'Test in Progress'),          
        ('Completed', 'Test Completed'),             
        ('Cancelled', 'Test Cancelled'),
        ('Pending', 'Pending')
    ]

    # Relations
    doctor = models.ForeignKey(
        DoctorProfile,              #  Each doctor has its own dashboard
        on_delete=models.CASCADE,
        related_name='ordered_tests',
        help_text="Doctor who ordered this test"
    )
    patient = models.ForeignKey(
        PatientProfile,            #  Each patient has its own dashboard
        on_delete=models.CASCADE,
        related_name='lab_tests',
        help_text="Patient who needs this test"
    )
    lab = models.ForeignKey(
        "accounts.LabProfile",   #  Each lab has its own dashboard
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="lab_tests"
    )

    # Test details
    test_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # Collection details
    sample_collection_address = models.TextField(
        blank=True, null=True,
        help_text="Patient address for sample collection"
    )

    # File upload by lab
    report_file = models.FileField(upload_to="lab_reports/", blank=True, null=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Suggested'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Laboratory Test'
        verbose_name_plural = 'Laboratory Tests'

    def __str__(self):
        return f"{self.test_name} for {self.patient.user.get_full_name()} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        from django.utils import timezone
        if self.status == 'Completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_completed(self):
        return self.status == 'Completed'
    
    
class Notification(models.Model):
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Generic foreign key fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-created_at']
        
class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, related_name='prescriptions', on_delete=models.CASCADE)
    file = models.FileField(upload_to='prescriptions/')
    uploaded_at = models.DateTimeField(auto_now_add=True)