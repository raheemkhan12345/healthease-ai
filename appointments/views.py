from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DoctorSignUpForm, PatientSignUpForm, DoctorLoginForm, PatientLoginForm
from accounts.models import User, DoctorProfile as Doctor, PatientProfile as Patient
from .models import Appointment
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import DoctorSearchForm, AppointmentForm
from accounts.models import User, DoctorProfile, PatientProfile
from .models import Appointment 
from django.core.paginator import Paginator
from .zoom import ZoomAPI
from django.db import transaction
from .models import Appointment, Notification 
from django.core.exceptions import ObjectDoesNotExist



def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')
968
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
    form = DoctorSearchForm()
    context = {
        'form': form,
        'specializations': DoctorProfile.SPECIALIZATION_CHOICES, 
    }
    return render(request, 'home.html', context)

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
                        date_of_birth=form.cleaned_data.get('date_of_birth')
                    )

                    login(request, user)
                    messages.success(request, 'Registration successful!')

                    # Handle redirect with 'next' parameter (for search)
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

    # Ensure this always runs in both POST (invalid) and GET
    return render(request, 'accounts/patient_signup.html', {'form': form})
  
# search doctors.

def doctor_search(request):
    form = DoctorSearchForm(request.GET or None)
    doctors = DoctorProfile.objects.select_related('user').all()

    specialization = request.GET.get('specialization')
    location = request.GET.get('location')
    query = request.GET.get('query')

    if specialization:
        doctors = doctors.filter(specialization=specialization)
    if location:
        doctors = doctors.filter(hospital__icontains=location)
    if query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(specialization__icontains=query)
        )

    # 🔒 Check login
@login_required(login_url='accounts:patient_signup')
def doctor_search(request):
    form = DoctorSearchForm(request.GET or None)
    doctors = DoctorProfile.objects.select_related('user').all()
    
    specialization = ''
    location = ''
    query = ''
    
    if form.is_valid():
        specialization = form.cleaned_data.get('specialization', '')
        location = form.cleaned_data.get('location', '')
        query = form.cleaned_data.get('query', '')

        # Save filters and redirect to signup if not authenticated
        if not request.user.is_authenticated:
            request.session['search_specialization'] = specialization
            request.session['search_location'] = location
            request.session['search_query'] = query
            return redirect('accounts:patient_signup')

        # Apply filters
        if specialization:
            doctors = doctors.filter(specialization=specialization)
        if location:
            doctors = doctors.filter(hospital__icontains=location)
        if query:
            doctors = doctors.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(specialization__icontains=query)
            )

    # Sort and paginate
    doctors = doctors.order_by('-experience')
    paginator = Paginator(doctors, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'doctors': page_obj,
        'specializations': DoctorProfile.SPECIALIZATION_CHOICES,
        'selected_specialization': specialization,
        'selected_location': location,
        'query': query
    }
    return render(request, 'appointments/doctor_list.html', context)


@login_required
def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            try:
                patient = request.user.patientprofile
            except ObjectDoesNotExist:
                messages.error(request, "Only patients can book appointments.")
                return redirect('appointments:doctor_detail', doctor_id=doctor.id)

            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.doctor = doctor

            # ✅ REMOVE Zoom code
            appointment.save()
            print("✅ Form submitted")
            messages.success(request, 'Appointment booked successfully!')
            return redirect('appointments:appointment_confirmation', appointment.id)
    else:
        form = AppointmentForm()

    return render(request, 'appointments/doctor_detail.html', {'doctor': doctor, 'form': form})

@login_required
def appointment_confirmation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'appointments/appointment_confirmation.html', {
        'appointment': appointment
    })

@login_required
def video_consultation(request, appointment_id):
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id,
        patient=request.user.patientprofile
    )
    
    if not appointment.zoom_join_url:
        messages.error(request, "No Zoom meeting link found for this appointment")
        return redirect('appointment_confirmation', appointment_id=appointment_id)
    
    # Check if the appointment time is within the next 15 minutes or has started
    appointment_datetime = datetime.combine(appointment.date, appointment.start_time)
    now = timezone.now()
    
    if now < appointment_datetime - timedelta(minutes=15):
        messages.warning(request, "Your consultation will begin at " + appointment_datetime.strftime("%I:%M %p"))
        return redirect('appointment_confirmation', appointment_id=appointment_id)
    
    return render(request, 'appointments/video_consultation.html', {
        'appointment': appointment,
        'now': now,
        'appointment_datetime': appointment_datetime
    })


@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)

    try:
        patient = request.user.patientprofile
    except PatientProfile.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('doctor_search')

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.doctor = doctor
            appointment.zoom_meeting_id = None
            appointment.zoom_join_url = None
            appointment.save()

            # Notifications
            Notification.objects.create(
                recipient=doctor.user,
                message=f"New appointment booked by {patient.user.username} for {appointment.date} at {appointment.start_time}."
            )
            Notification.objects.create(
                recipient=patient.user,
                message=f"Your appointment with Dr. {doctor.user.username} is booked for {appointment.date} at {appointment.start_time}."
            )

            messages.success(request, 'Your appointment has been booked successfully!')
            return redirect('appointment_confirmation', appointment.id)
        else:
            # Invalid form — show errors
            messages.error(request, "Please correct the errors in the form.")
            return render(request, 'appointments/book_appointment.html', {
                'form': form,
                'doctor': doctor,
            })

    else:
        form = AppointmentForm()

    return render(request, 'appointments/book_appointment.html', {
        'form': form,
        'doctor': doctor,
    })

def home(request):
    SPECIALIZATION_CHOICES = [
    ('Cardiologist', 'Cardiologist'),
    ('Dermatologist', 'Dermatologist'),
    ('Neurologist', 'Neurologist'),
    ('Pediatrician', 'Pediatrician'),
    ('Orthopedic', 'Orthopedic'),
    ('Gynecologist', 'Gynecologist'),
    ('General Physician', 'General Physician'),
    ('ENT Specialist', 'ENT Specialist'),
]

    SPECIALIZATION_ICONS = {
    'Cardiologist': 'fa-heart-pulse',
    'Dermatologist': 'fa-syringe',
    'Neurologist': 'fa-brain',
    'Pediatrician': 'fa-baby',
    'Orthopedic': 'fa-bone',
    'Gynecologist': 'fa-venus',
    'General Physician': 'fa-user-doctor',
    'ENT Specialist': 'fa-ear-listen',
}

    specializations_with_icons = []
    for value, label in SPECIALIZATION_CHOICES:
        icon = SPECIALIZATION_ICONS.get(value, 'fa-user-md')
        specializations_with_icons.append((value, label, icon))

    return render(request, 'home.html', {
        'specializations': SPECIALIZATION_CHOICES,                # for dropdown (2 values)
        'specializations_with_icons': specializations_with_icons  # for cards (3 values)
    })