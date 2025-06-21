from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms
from .models import Appointment
from django.utils import timezone
from datetime import datetime, timedelta

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
    
    


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return date
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        
        if date and time:
            appointment_datetime = datetime.combine(date, time)
            if appointment_datetime < timezone.now():
                raise forms.ValidationError("Appointment time cannot be in the past.")
        
        return cleaned_data
    
    
    
    