from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from .models import DoctorProfile, PatientProfile
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse

from django.contrib.auth.forms import UserCreationForm
from .models import User

import re

User = get_user_model()

# ─────────────────── Doctor Signup ─────────────────── #
class DoctorSignUpForm(UserCreationForm):
    specialization = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Cardiology, Neurology, etc.'}),
        required=True
    )
    hospital = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Location or Hospital'}),
        required=True
    )
    experience = forms.IntegerField(
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={'min': '0'}),
        required=True
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'}),
        help_text='Optional. JPG or PNG, max 2MB'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'\d', password1):
            raise forms.ValidationError("Password must contain at least one number.")
        if not re.search(r'[^A-Za-z0-9]', password1):
            raise forms.ValidationError("Password must contain at least one special character.")
        return password1

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'doctor'
        if commit:
            user.save()
            DoctorProfile.objects.create(
                user=user,
                specialization=self.cleaned_data['specialization'],
                hospital=self.cleaned_data['hospital'],
                experience=self.cleaned_data['experience'],
                profile_picture=self.cleaned_data.get('profile_picture') or 'default.jpg'
            )
        return user

# ─────────────────── Patient Signup ─────────────────── #

User = get_user_model()

class PatientSignUpForm(UserCreationForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'date_of_birth']

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        if not re.search(r'\d', password1):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[^A-Za-z0-9]', password1):
            raise forms.ValidationError("Password must contain at least one special character.")
        return password1

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'patient'
        if commit:
            user.save()
            PatientProfile.objects.create(user=user)
        return user

class DoctorLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class PatientLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
