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


def doctor_signup(request):
    if request.user.is_authenticated:
        return redirect('doctor_dashboard')
        
    if request.method == 'POST':
        form = DoctorSignUpForm(request.POST)
        if form.is_valid():
            try:
                if User.objects.filter(email=form.cleaned_data['email']).exists():
                    form.add_error('email', 'This email is already registered')
                elif User.objects.filter(username=form.cleaned_data['username']).exists():
                    form.add_error('username', 'This username is taken')
                else:
                    user = form.save()
                    login(request, user)
                    return redirect('doctor_dashboard')
            except Exception as e:
                form.add_error(None, f"Account creation failed: {str(e)}")
        # Remove this else clause completely - let it fall through to render at bottom
    else:
        form = DoctorSignUpForm()
    
    # Single return statement at the end
    return render(request, 'accounts/doctor_signup.html', {'form': form})
def patient_signup(request):
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_patient = True
            user.save()
            
            PatientProfile.objects.create(
                user=user,
                date_of_birth=form.cleaned_data['date_of_birth']
            )
            login(request, user)
            return redirect('patient_dashboard')
    else:
        form = PatientSignUpForm()
    return render(request, 'accounts/patient_signup.html', {'form': form})


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