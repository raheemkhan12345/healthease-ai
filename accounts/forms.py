from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, DoctorProfile, PatientProfile

from django.db import transaction
from django.db.utils import IntegrityError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, DoctorProfile, PatientProfile

class DoctorSignUpForm(UserCreationForm):
    specialization = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Cardiology, Neurology, etc.'})
    )
    hospital = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Hospital name'})
    )
    experience = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'min': '0',
            'max': '70',
            'placeholder': 'Years of experience'
        }),
        error_messages={
            'required': 'Years of experience is required',
            'invalid': 'Please enter a whole number between 0 and 70'
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['password1'].widget.attrs['minlength'] = 4

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_doctor = True
        
        if commit:
            try:
                with transaction.atomic():
                    user.save()
                    # Create and save the doctor profile with all data
                    DoctorProfile.objects.create(
                        user=user,
                        specialization=self.cleaned_data['specialization'],
                        hospital=self.cleaned_data['hospital'],
                        experience=self.cleaned_data['experience']
                    )
            except IntegrityError as e:
                raise forms.ValidationError(
                    "Could not create doctor profile. Please try again."
                ) from e
            
        return user
class PatientSignUpForm(UserCreationForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'date_of_birth')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_patient = True
        if commit:
            user.save()
            PatientProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data['date_of_birth']
            )
        return user

class DoctorLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class PatientLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    
    