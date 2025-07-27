from django import forms
from .models import LabTest
from django.contrib.auth.forms import UserCreationForm
from .models import Appointment
from django.utils import timezone
from datetime import datetime, timedelta
from datetime import time
from .models import User, Appointment
from accounts.models import DoctorProfile
from django.core.exceptions import ValidationError



class DoctorSignUpForm(UserCreationForm):
    # Add doctor-specific fields
    pass

class PatientSignUpForm(UserCreationForm):
    # Add patient-specific fields
    pass

class DoctorLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class PatientLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    
    
# search doctors.

class DoctorSearchForm(forms.Form):
    specialization = forms.ChoiceField(
        required=False,
        label='Specialization'
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Location or hospital'})
    )
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search by name'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Use fixed choices from model — not from database
        choices = [('', 'All Specializations')] + list(DoctorProfile.SPECIALIZATION_CHOICES)
        self.fields['specialization'].choices = choices


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'start_time', 'reason']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Briefly describe your symptoms or reason for appointment'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)

        today = timezone.now().date()
        self.fields['date'].widget = forms.DateInput(attrs={
            'type': 'date',
            'min': today.strftime('%Y-%m-%d'),  # Allow today and future
        })

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise ValidationError("Appointment date cannot be in the past.")
        return date

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        if start_time < time(9, 0) or start_time > time(17, 0):
            raise ValidationError("Appointments must be between 9 AM and 5 PM")
        return start_time


class LabTestForm(forms.ModelForm):
    TEST_CHOICES = [
        ('Blood Sugar', 'Blood Sugar'),
        ('Urine Test', 'Urine Test'),
        ('CBC', 'CBC (Complete Blood Count)'),
        ('Liver Function', 'Liver Function Test'),
        ('Thyroid', 'Thyroid Test'),
    ]

    test_name = forms.ChoiceField(
        choices=TEST_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        label="Select Test Type"
    )

    class Meta:
        model = LabTest
        fields = ['test_name']

class PatientLabDetailsForm(forms.ModelForm):
    
    LAB_CHOICES = [
        ('', '--- Select Lab ---'),
        ('City Lab', 'City Lab'),
        ('Shifa Diagnostics', 'Shifa Diagnostics'),
        ('Excel Lab', 'Excel Lab'),
    ]

    lab_name = forms.ChoiceField(
        choices=LAB_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        }),
        help_text="Select your preferred lab facility"
    )

    sample_collection_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Full address including city and postal code'
        }),
        help_text="Where should the lab collect the sample?"
    )

    

    class Meta:
        model = LabTest
        fields = ['lab_name', 'sample_collection_address']
        labels = {
            'sample_collection_address': 'Collection Address'
        }

    def clean_lab_name(self):
        lab_name = self.cleaned_data.get('lab_name')
        if not lab_name:
            raise ValidationError("Please select a lab facility")
        return lab_name

   

class LabReportUploadForm(forms.ModelForm):
    """
    Form for labs to upload test results (final step)
    """
    report_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.png,.docx'
        }),
        help_text="Upload test results (PDF, JPG, PNG, or DOCX)"
    )

    notes_for_doctor = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Any special notes for the doctor...'
        })
    )

    class Meta:
        model = LabTest
        fields = ['report_file', 'notes_for_doctor']
        labels = {
            'notes_for_doctor': 'Lab Notes'
        }