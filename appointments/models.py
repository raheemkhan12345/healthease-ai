from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import DoctorProfile, PatientProfile, TimeSlot
from datetime import datetime, timedelta, timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


User = get_user_model()  # This ensures the correct User model is used

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
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


class LabTest(models.Model):
    # Lab choices - predefined list of available labs
    LAB_CHOICES = [
        ('City Lab', 'City Lab'),
        ('Shifa Diagnostics', 'Shifa Diagnostics'),
        ('Excel Lab', 'Excel Lab'),
    ]
    

    # Test stages - more granular status tracking
    STATUS_CHOICES = [
        ('Suggested', 'Suggested by Doctor'),       # Doctor suggested test
        ('Details Pending', 'Patient Details Needed'), # Waiting for patient info
        ('Sent to Lab', 'Sent to Laboratory'),      # Details complete, sent to lab
        ('Sample Collected', 'Sample Collected'),   # Lab collected sample
        ('In Progress', 'Test in Progress'),        # Lab processing test
        ('Completed', 'Test Completed'),           # Results available
        ('Cancelled', 'Test Cancelled'),           # Test cancelled
    ]

    # Test name - required field
    test_name = models.CharField(
        max_length=255,
        help_text="Name of the laboratory test to be performed"
    )

    report_file = models.FileField(upload_to='lab_reports/', null=True, blank=True)

    # Patient relationship - who the test is for
    patient = models.ForeignKey(
        PatientProfile, 
        on_delete=models.CASCADE,
        related_name='lab_tests',
        help_text="Patient who needs this test"
    )

    # Doctor relationship - who ordered the test
    doctor = models.ForeignKey(
        DoctorProfile, 
        on_delete=models.CASCADE,
        related_name='ordered_tests',
        help_text="Doctor who ordered this test"
    )

    # Lab selection - where test will be performed
    lab_name = models.CharField(
        max_length=255, 
        choices=LAB_CHOICES, 
        blank=True, 
        null=True,
        help_text="Laboratory facility where test will be conducted"
    )

    # Test status - tracks progress through workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Suggested',
        help_text="Current status of the test in the workflow"
    )

    # Test results - file upload for reports
    report_file = models.FileField(upload_to='lab_reports/', blank=True, null=True)


    # Collection address - where sample will be collected
    sample_collection_address = models.TextField(
        blank=True, 
        null=True,
        help_text="Complete address for sample collection"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the test was initially suggested"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the test record was last updated"
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the test was marked as completed"
    )



    class Meta:
        ordering = ['-created_at']  # Newest tests first by default
        verbose_name = 'Laboratory Test'
        verbose_name_plural = 'Laboratory Tests'

    def __str__(self):
        return f"{self.test_name} for {self.patient.user.get_full_name()} (Status: {self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Automatically set completed_at when status changes to Completed
        if self.status == 'Completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('appointments:lab_test_detail', args=[str(self.id)])

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