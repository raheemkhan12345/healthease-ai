from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms
from .models import Appointment
from django.utils import timezone
from datetime import datetime, timedelta
from datetime import time

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
    specialization = forms.CharField(required=False)
    location = forms.CharField(required=False)
    query = forms.CharField(required=False, label='Search')

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'patient', 'date', 'start_time', 'end_time', 'reason', 'status', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date', 
                'min': timezone.now().date()
            }),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise forms.ValidationError("Appointment date cannot be in the past")
        return date

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        if start_time < time(9, 0) or start_time > time(17, 0):
            raise forms.ValidationError("Appointments must be between 9 AM and 5 PM")
        return start_time