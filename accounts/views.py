from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import DoctorSignUpForm, PatientSignUpForm, DoctorLoginForm, PatientLoginForm
from .models import DoctorProfile, PatientProfile, User
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import DoctorProfile
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from .models import User 

def doctor_signup(request):
    if request.method == 'POST':
        form = DoctorSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('accounts:doctor_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DoctorSignUpForm()
    return render(request, 'accounts/doctor_signup.html', {'form': form})

@login_required
def doctor_dashboard(request):
    if not request.user.user_type == 'doctor':
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('accounts:user_logout')
    
    try:
        profile = DoctorProfile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('accounts:user_logout')
    
    # You'll need to implement appointments logic based on your app
    appointments = []  # Replace with actual appointments query
    
    context = {
        'doctor': request.user,
        'profile': profile,
        'appointments': appointments,
    }
    return render(request, 'doctor_dashboard.html', context)

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')  #  your home URL name
def patient_signup(request):
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('patient_dashboard')  # Update with your patient dashboard URL
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientSignUpForm()
    return render(request, 'accounts/patient_signup.html', {'form': form})

@login_required
def patient_dashboard(request):
    if not request.user.user_type == 'patient':
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('accounts:user_logout')
    
    try:
        profile = request.user.patientprofile
    except:
        profile = None
    
    context = {
        'patient': request.user,
        'profile': profile,
    }
    return render(request, 'patient_dashboard.html', context)

def doctor_login(request):
    if request.user.is_authenticated and request.user.is_doctor:
        return redirect('accounts:doctor_dashboard')
        
    if request.method == 'POST':
        form = DoctorLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.is_doctor:
                login(request, user)
                messages.success(request, f'Welcome, Dr. {user.username}!')
                return redirect('accounts:doctor_dashboard')
            else:
                messages.error(request, 'Invalid credentials or not a doctor account')
    else:
        form = DoctorLoginForm()
    return render(request, 'accounts/doctor_login.html', {'form': form})

def patient_login(request):
    if request.user.is_authenticated and request.user.is_patient:
        return redirect('accounts:patient_dashboard')
        
    if request.method == 'POST':
        form = PatientLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.is_patient:
                login(request, user)
                messages.success(request, f'Welcome, {user.username}!')
                return redirect('accounts:patient_dashboard')
            else:
                messages.error(request, 'Invalid credentials or not a patient account')
    else:
        form = PatientLoginForm()
    return render(request, 'accounts/patient_login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('chat:home')

@login_required
def doctor_dashboard(request):
    if not request.user.is_doctor:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('chat:home')
    
    # Get doctor profile or create if doesn't exist
    doctor_profile, created = DoctorProfile.objects.get_or_create(user=request.user)
    
    context = {
        'doctor': request.user,
        'profile': doctor_profile,
        'appointments': request.user.doctor_appointments.all()[:5]  # Example of related data
    }
    return render(request, 'accounts/doctor_dashboard.html', context)

@login_required
def patient_dashboard(request):
    if not request.user.is_patient:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('chat:home')
    
    # Get patient profile or create if doesn't exist
    patient_profile, created = PatientProfile.objects.get_or_create(user=request.user)
    
    context = {
        'patient': request.user,
        'profile': patient_profile,
        'appointments': request.user.patient_appointments.all()[:5]  # Example of related data
    }
    return render(request, 'accounts/patient_dashboard.html', context)

@login_required
def doctor_profile(request):
    if not request.user.is_doctor:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('chat:home')
    
    # Get or create doctor profile
    doctor_profile, created = DoctorProfile.objects.get_or_create(user=request.user)
    
    context = {
        'doctor': request.user,
        'profile': doctor_profile
    }
    return render(request, 'accounts/doctor_profile.html', context)

@login_required
def patient_profile(request):
    if not request.user.is_patient:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('chat:home')
    
    # Get or create patient profile
    patient_profile, created = PatientProfile.objects.get_or_create(user=request.user)
    
    context = {
        'patient': request.user,
        'profile': patient_profile
    }
    return render(request, 'accounts/patient_profile.html', context)

# doctor selection fucntionality.


def doctor_search(request):
    query = request.GET.get('q')
    specialization = request.GET.get('specialization')
    
    doctors = DoctorProfile.objects.all()
    
    if query:
        doctors = doctors.filter(
            Q(user__username__icontains=query) |
            Q(hospital__icontains=query)
        )
    
    if specialization:
        doctors = doctors.filter(specialization=specialization)
    
    specializations = DoctorProfile.objects.values_list(
        'specialization', flat=True
    ).distinct()
    
    return render(request, 'doctor_search.html', {
        'doctors': doctors,
        'specializations': specializations
    })