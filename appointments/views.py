from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DoctorSignUpForm, PatientSignUpForm, DoctorLoginForm, PatientLoginForm
from .models import User, Doctor, Patient, Appointment
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import DoctorSearchForm, AppointmentForm
from accounts.models import User, DoctorProfile, PatientProfile
from .models import Appointment 
from django.core.paginator import Paginator
from .zoom import ZoomAPI

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
  
# search doctors.

def doctor_search(request):
    query = request.GET.get('q')
    specialization = request.GET.get('specialization')
    location = request.GET.get('location')
    
    doctors = DoctorProfile.objects.select_related('user').all()
    
    if query:
        doctors = doctors.filter(
            Q(user__username__icontains=query) |
            Q(hospital__icontains=query) |
            Q(specialization__icontains=query)
        )
    
    if specialization:
        doctors = doctors.filter(specialization=specialization)
    
    if location:
        doctors = doctors.filter(hospital__icontains=location)
    
    # Get all specializations for filter
    specializations = DoctorProfile.SPECIALIZATION_CHOICES
    
    paginator = Paginator(doctors, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'appointments/doctor_list.html', {
        'doctors': page_obj,
        'specializations': specializations,
        'selected_specialization': specialization,
        'selected_location': location,
        'query': query
    })

def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    return render(request, 'appointments/doctor_detail.html', {
        'doctor': doctor
    })
    
    
    
@login_required
def book_appointment(request, doctor_id):
     if request.method == 'POST':
        doctor = get_object_or_404(DoctorProfile, id=doctor_id)
        patient = request.user.patientprofile
        
        date = request.POST.get('date')
        time_str = request.POST.get('time')
        reason = request.POST.get('reason')
        
        try:
            # Create appointment
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=date,
                start_time=time_str,
                reason=reason
            )
            
            # Create Zoom meeting
            zoom = ZoomAPI()
            start_datetime = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
            meeting = zoom.create_meeting(
                topic=f"Consultation with Dr. {doctor.user.username}",
                start_time=start_datetime
            )
            
            # Update appointment with Zoom details
            appointment.zoom_meeting_id = meeting.get('id')
            appointment.zoom_join_url = meeting.get('join_url')
            appointment.save()
            
            messages.success(request, 'Your appointment has been booked successfully!')
            return redirect('appointment_confirmation', appointment.id)
            
        except Exception as e:
            messages.error(request, f'Error booking appointment: {str(e)}')
            return redirect('doctor_detail', doctor_id=doctor.id)
    
     return redirect('doctor_search')

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