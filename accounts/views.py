from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction
import notifications
from .forms import DoctorSignUpForm, PatientSignUpForm, DoctorLoginForm, PatientLoginForm
from .models import DoctorProfile, PatientProfile, User
from appointments.models import Appointment, LabTest, Notification

from appointments.models import Appointment
from django.utils import timezone
from django.utils.timezone import make_aware

# ─────────────── Signup Views ─────────────── #
def doctor_signup(request):
    if request.method == 'POST':
        form = DoctorSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.user_type = 'doctor'
                    user.save()

                    DoctorProfile.objects.create(
                        user=user,
                        specialization=form.cleaned_data['specialization'],
                        hospital=form.cleaned_data['hospital'],
                        experience=form.cleaned_data['experience'],
                        profile_picture=form.cleaned_data.get('profile_picture')
                    )

                    login(request, user)
                    messages.success(request, 'Registration successful!')
                    return redirect('accounts:doctor_dashboard')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DoctorSignUpForm()
    return render(request, 'accounts/doctor_signup.html', {'form': form})


def patient_signup(request):
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.user_type = 'patient'
                    user.save()

                    PatientProfile.objects.create(
                        user=user,
                        date_of_birth=form.cleaned_data.get('date_of_birth'),
                         address=form.cleaned_data.get('address')
                        
                    )

                    login(request, user)
                    messages.success(request, 'Registration successful!')

                    # ✅ Handle redirect with ?next=...
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('home')

            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientSignUpForm()

    return render(request, 'accounts/patient_signup.html', {'form': form})



# ─────────────── Login Views ─────────────── #
def doctor_login(request):
    if request.user.is_authenticated and request.user.user_type == 'doctor':
        return redirect('accounts:doctor_dashboard')
    
    if request.method == 'POST':
        form = DoctorLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user and user.user_type == 'doctor':
                login(request, user)
                messages.success(request, f'Welcome, Dr. {user.username}!')
                return redirect('accounts:doctor_dashboard')
            else:
                messages.error(request, 'Invalid credentials or not a doctor account')
    else:
        form = DoctorLoginForm()
    return render(request, 'accounts/doctor_login.html', {'form': form})


def patient_login(request):
    if request.user.is_authenticated and request.user.user_type == 'patient':
        return redirect('accounts:patient_dashboard')

    if request.method == 'POST':
        form = PatientLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user and user.user_type == 'patient':
                login(request, user)
                messages.success(request, f'Welcome, {user.username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials or not a patient account')
    else:
        form = PatientLoginForm()
    return render(request, 'accounts/patient_login.html', {'form': form})

# ─────────────── Logout ─────────────── #
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

# ─────────────── Dashboards ─────────────── #



@login_required
def doctor_dashboard(request):
    if request.user.user_type != 'doctor':
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('home')

    profile, _ = DoctorProfile.objects.get_or_create(user=request.user)
    appointments = Appointment.objects.filter(doctor=profile).order_by('-date', '-start_time')
    now = timezone.localtime()

    upcoming_consultations = []

    for appt in appointments:
        appt_datetime = make_aware(datetime.combine(appt.date, appt.start_time))
        join_window_start = appt_datetime - timedelta(minutes=15)  # 15 min before
        join_window_end = appt_datetime + timedelta(minutes=45)    # 30 min consultation + 15 min after

        if appt.status.lower() == 'approved' and join_window_start <= now <= join_window_end:
            upcoming_consultations.append(appt)

    context = {
        'doctor': request.user,
        'profile': profile,
        'appointments': appointments,
        'patient_count': appointments.values('patient').distinct().count(),
        'upcoming_consultations': upcoming_consultations,
        'today': now.date(),
        'now': now.time(),
    }

    return render(request, 'accounts/doctor_dashboard.html', context)


@login_required
def patient_dashboard(request):
    try:
        patient = request.user.patientprofile
    except PatientProfile.DoesNotExist:
        messages.error(request, "⚠️ You must have a patient account to access the patient dashboard.")
        return redirect("accounts:doctor_dashboard")  # ya koi safe page (home/doctor_dashboard)

    appointments = Appointment.objects.filter(patient=patient).order_by('-date')[:5]
    lab_tests = LabTest.objects.filter(patient=patient)
    now = timezone.localtime()

    upcoming_consultations = []
    approved_appointments = []

    # Patient ke liye notifications fetch karo
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)

    for appt in appointments:
        appt_datetime = make_aware(datetime.combine(appt.date, appt.start_time))
        join_window_start = appt_datetime - timedelta(minutes=15)
        join_window_end = appt_datetime + timedelta(minutes=45)

        if appt.status.lower() == 'approved' and join_window_start <= now <= join_window_end:
            upcoming_consultations.append(appt)

        if appt.status.lower() == 'approved' and appt_datetime > now:
            approved_appointments.append(appt)

    return render(request, 'accounts/patient_dashboard.html', {
        'appointments': appointments,
        'lab_tests': lab_tests,
        'upcoming_consultations': upcoming_consultations,
        'approved_appointments': approved_appointments,
        'notifications': notifications,  
        'today': now.date(),
        'now': now.time(),
    })


# ─────────────── Profiles ─────────────── #
@login_required
def doctor_profile(request):
    if request.user.user_type != 'doctor':
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('home')

    profile, _ = DoctorProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/doctor_profile.html', {'doctor': request.user, 'profile': profile})


@login_required
def patient_profile(request):
    if request.user.user_type != 'patient':
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('home')

    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/patient_profile.html', {'patient': request.user, 'profile': profile})

# ─────────────── Doctor Search ─────────────── #
def doctor_search(request):
    query = request.GET.get('q', '')
    specialization = request.GET.get('specialization', '')

    doctors = DoctorProfile.objects.all()

    if query:
        doctors = doctors.filter(Q(user__username__icontains=query) | Q(hospital__icontains=query))

    if specialization:
        doctors = doctors.filter(specialization__iexact=specialization)

    specializations = DoctorProfile.objects.values_list('specialization', flat=True).distinct()

    return render(request, 'doctor_search.html', {
        'doctors': doctors,
        'specializations': specializations
    })



