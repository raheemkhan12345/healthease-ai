from django import forms
from django.contrib.auth.forms import UserCreationForm
from django import forms
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
            'date': forms.DateInput(attrs={
                'type': 'date',
                'min': timezone.now().date()
            }),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Briefly describe your symptoms or reason for appointment'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise ValidationError("Start time cannot be in the past.")
        return date

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        if start_time < time(9, 0) or start_time > time(17, 0):
            raise ValidationError("Appointments must be between 9 AM and 5 PM")
        return start_time
    