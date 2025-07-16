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

        tomorrow = timezone.now().date() + timedelta(days=1)
        self.fields['date'].widget = forms.DateInput(attrs={
            'type': 'date',
            'min': tomorrow.strftime('%Y-%m-%d'),
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
        label="Test Name",
        widget=forms.Select(attrs={
            'class': 'form-select rounded-pill shadow-sm'
        })
    )

    class Meta:
        model = LabTest
        fields = ['test_name', 'lab_name', 'sample_collection_address']
        widgets = {
            'lab_name': forms.Select(attrs={
                'class': 'form-select rounded-pill shadow-sm'
            }),
            'sample_collection_address': forms.TextInput(attrs={
                'class': 'form-control rounded-pill shadow-sm',
                'placeholder': 'Enter collection address'
            }),
        }

    