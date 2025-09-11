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
    start_time = forms.ChoiceField()

    class Meta:
        model = Appointment
        fields = ['date', 'start_time', 'transaction_id']
        widgets = {
            'transaction_id': forms.TextInput(attrs={
                'placeholder': 'Enter your payment Transaction ID',
                'class': 'form-control',
                'maxlength': '11'  # ✅ HTML level restriction
            }),
        }

    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop("doctor", None)  
        super(AppointmentForm, self).__init__(*args, **kwargs)

        today = timezone.now().date()
        self.fields['date'].widget = forms.DateInput(attrs={
            'type': 'date',
            'min': today.strftime('%Y-%m-%d'),
            'class': 'form-control'
        })

        # ✅ Time slot generation
        time_choices = []
        start = datetime.strptime("09:00", "%H:%M")
        end = datetime.strptime("20:00", "%H:%M")
        step = timedelta(minutes=30)

        while start <= end:
            formatted_label = start.strftime("%I:%M %p")
            value = start.strftime("%H:%M")
            time_choices.append((value, formatted_label))
            start += step

        self.fields['start_time'] = forms.ChoiceField(
            choices=[('', 'Select Time')] + time_choices,
            required=True,
            widget=forms.Select(attrs={'class': 'form-control'})
        )

    def clean_transaction_id(self):
        transaction_id = self.cleaned_data.get("transaction_id")

        if not transaction_id:
            raise ValidationError("⚠️ Please enter your Transaction ID after payment.")

        if not transaction_id.isdigit():
            raise ValidationError("⚠️ Transaction ID must contain only numbers.")

        if len(transaction_id) != 11:
            raise ValidationError("⚠️ Transaction ID must be exactly 11 digits long.")

        return transaction_id

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        start_time = cleaned_data.get("start_time")

        if date and date < timezone.now().date():
            raise forms.ValidationError("⚠️ Please select a future date (not today).")

        if date and start_time and self.doctor:
            start_dt = datetime.combine(date, datetime.strptime(start_time, "%H:%M").time())
            end_dt = start_dt + timedelta(minutes=30)

            conflict = Appointment.objects.filter(
                doctor=self.doctor,
                date=date,
                start_time__lt=end_dt.time(),
                end_time__gt=start_dt.time(),
                status__in=["pending", "confirmed", "approved"]
            ).exists()

            if conflict:
                formatted_date = date.strftime("%B %d, %Y")
                formatted_time = datetime.strptime(start_time, "%H:%M").strftime("%I:%M %p")
                raise forms.ValidationError(
                    f"❌ The slot {formatted_time} on {formatted_date} is already booked. "
                    f"Please choose another time or try the next day."
                )

        return cleaned_data

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
        ('city lab', 'city lab'),
        ('shifa diagnostics', 'shifa diagnostics'),
        ('excel lab', 'excel lab'),
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
        
    

