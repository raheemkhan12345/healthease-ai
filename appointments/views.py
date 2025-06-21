from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DoctorSignUpForm, PatientSignUpForm, DoctorLoginForm, PatientLoginForm
from .models import User, Doctor, Patient, Appointment

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def contact(request):
    return render(request, 'contact.html')

def landing_page(request):
    return render(request,'landing.urls')

def doctor_signup(request):
    return render(request,'doctor_signup.urls')
def patient_signup(request):
    return render(request,'patient_signup.urls')

def doctor_dashboard(request):
    return render(request,'doctor_dashboad')
def patient_dashboard(request):
    return render(request,'patient_dashboad')
def doctor_profile(request):
    return render(request,'doctor_profile')
def patient_profile(request):
    return render(request,'patient_profile')


def doctor_login(request):
    if request.user.is_authenticated and request.user.is_doctor:
        return redirect('doctor_dashboard')
    
    if request.method == 'POST':
        form = DoctorLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_doctor:
                login(request, user)
                return redirect('doctor_dashboard')
            else:
                messages.error(request, 'Invalid doctor credentials')
    else:
        form = DoctorLoginForm()
    return render(request, 'auth/doctor_login.html', {'form': form})

def patient_login(request):
    if request.user.is_authenticated and request.user.is_patient:
        return redirect('patient_dashboard')
    
    if request.method == 'POST':
        form = PatientLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_patient:
                login(request, user)
                return redirect('patient_dashboard')
            else:
                messages.error(request, 'Invalid patient credentials')
    else:
        form = PatientLoginForm()
    return render(request, 'auth/patient_login.html', {'form': form})

# Keep your existing signup views as they are

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to patient login after logout

# Remove the index view or keep it as a redirect if needed

def home(request):
    if request.user.is_authenticated:
        if request.user.is_doctor:
            return redirect('doctor_dashboard')
        else:
            return redirect('patient_dashboard')
    return render(request, 'auth/landing.html')

def patient_signup(request):
    # Your patient registration implementation
    form = PatientSignUpForm()
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('patient_dashboard')
    return render(request, 'registration/patient_signup.html', {'form': form})



