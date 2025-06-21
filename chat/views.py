from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import DoctorSignUpForm, PatientSignUpForm

# Main Pages
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def contact(request):
    return render(request, 'contact.html')


def doctor_dashboard(request):
    return render(request,'doctor_dashboard.urls')
def patient_dashboard(request):
    return render(request,'patient_dashboard.urls')
def doctor_profile(request):
    return render(request,'doctor_profile.urls')
def patient_profile(request):
    return render(request,'patient_profile.urls')

