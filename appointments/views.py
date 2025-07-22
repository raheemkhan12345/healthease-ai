from venv import logger
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import  DoctorSignUpForm, LabReportUploadForm, PatientLabDetailsForm, PatientSignUpForm, DoctorLoginForm, PatientLoginForm
from accounts.models import User, DoctorProfile as Doctor, PatientProfile as Patient
from .models import Appointment
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import DoctorSearchForm, AppointmentForm
from accounts.models import User, DoctorProfile, PatientProfile
from .models import Appointment,LabTest 
from django.core.paginator import Paginator
from .zoom import ZoomAPI
from django.db import transaction
from .models import Appointment, Notification 
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .forms import LabTestForm as DoctorLabTestSuggestionForm
from django.core.exceptions import PermissionDenied
from datetime import date



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
    return render(request, 'accounts/doctor_dashboard.html')
def patient_dashboard(request):
    return render(request,'accounts/patient_dashboard.html')
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

        # Save filters for future use if not logged in (precaution)
        if not request.user.is_authenticated:
            request.session['search_specialization'] = specialization
            request.session['search_location'] = location
            request.session['search_query'] = query
            return redirect('accounts:patient_signup')

        # Combine filters using Q()
        filters = Q()
        if specialization:
            filters &= Q(specialization=specialization)
        if location:
            filters &= Q(hospital__icontains=location)
        if query:
            filters &= (
                Q(user__username__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
            )

        doctors = doctors.filter(filters)

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
    try:
        # Ensure only the correct patient can access this consultation
        appointment = get_object_or_404(
            Appointment,
            id=appointment_id,
            patient=request.user.patientprofile
        )
    except:
        messages.error(request, "You are not authorized to access this consultation.")
        return redirect('appointments:patient_dashboard')

    # ✅ Ensure appointment is confirmed
    if appointment.status != "confirmed":
        messages.error(request, "This appointment has not been confirmed yet.")
        return redirect('appointments:appointment_confirmation', appointment_id=appointment_id)

    # ✅ Ensure Zoom link is set
    if not appointment.zoom_join_url:
        messages.error(request, "No Zoom meeting link found for this appointment.")
        return redirect('appointments:appointment_confirmation', appointment_id=appointment_id)

    # ✅ Time check - allow only within 15 minutes before scheduled time
    appointment_datetime = datetime.combine(appointment.date, appointment.start_time)
    now = timezone.now()

    # Convert naive `appointment_datetime` to timezone-aware
    appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

    if now < appointment_datetime - timedelta(minutes=15):
        messages.warning(request, f"Your consultation will begin at {appointment_datetime.strftime('%I:%M %p')}")
        return redirect('appointments:appointment_confirmation', appointment_id=appointment_id)

    # ✅ Everything good — show consultation page
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
        return redirect('appointments:doctor_search')

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.doctor = doctor
            appointment.save()

            # ✅ Create Zoom meeting
            try:
                zoom = ZoomAPI()
                start_datetime = datetime.combine(appointment.date, appointment.start_time)
                meeting = zoom.create_meeting(
                    topic=f"Consultation with Dr. {doctor.user.username}",
                    start_time=start_datetime,
                    duration=30
                )
                appointment.zoom_meeting_id = meeting['id']
                appointment.zoom_join_url = meeting['join_url']
                appointment.save()
            except Exception as e:
                messages.error(request, f"Zoom meeting creation failed: {e}")
                return redirect('appointments:doctor_dashboard')

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
            messages.error(request, "Please correct the errors in the form.")
            return render(request, 'appointments/book_appointment.html', {
                'form': form,
                'doctor': doctor,
            })

    else:
        form = AppointmentForm()

@login_required
def approve_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Ensure only the correct doctor approves their own appointment
    if appointment.doctor.user != request.user:
        messages.error(request, "You are not authorized to approve this appointment.")
        return redirect('accounts:doctor_dashboard')

    appointment.status = 'Approved'
    appointment.save()
    messages.success(request, "Appointment approved successfully.")
    return redirect('accounts:doctor_dashboard')

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
      ('lab', 'Lab Tests')
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
    'lab': 'fa-vials',
}

    specializations_with_icons = []
    for value, label in SPECIALIZATION_CHOICES:
        icon = SPECIALIZATION_ICONS.get(value, 'fa-user-md')
        specializations_with_icons.append((value, label, icon))

    return render(request, 'home.html', {
        'specializations': SPECIALIZATION_CHOICES,                # for dropdown (2 values)
        'specializations_with_icons': specializations_with_icons  # for cards (3 values)
    })
    
    
@require_GET
def autocomplete_suggestions(request):
     term = request.GET.get('term', '').strip()
     field = request.GET.get('field')

     if not term or field not in ['location', 'query']:
        return JsonResponse([], safe=False)

     suggestions = set()

     if field == 'location':
        suggestions.update(
            DoctorProfile.objects.filter(hospital__icontains=term)
            .values_list('hospital', flat=True)
        )
     elif field == 'query':
        suggestions.update(
            DoctorProfile.objects.filter(
                Q(user__first_name__icontains=term) |
                Q(user__last_name__icontains=term)
            ).values_list('user__first_name', flat=True)
        )

     return JsonResponse(list(suggestions), safe=False)
 

 
@login_required
def suggest_lab_test(request, patient_id):
    patient = get_object_or_404(PatientProfile, id=patient_id)
    doctor = request.user.doctorprofile

    if request.method == 'POST':
        form = DoctorLabTestSuggestionForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    lab_test = form.save(commit=False)
                    lab_test.patient = patient
                    lab_test.doctor = doctor
                    lab_test.status = 'Suggested'
                    lab_test.save()

                    Notification.objects.create(
                        recipient=patient.user,
                        message=f"Dr. {doctor.user.get_full_name()} suggested a {lab_test.test_name} test."
                    )
                    messages.success(request, "Lab test suggested successfully!")
                    return redirect('appointments:doctor_dashboard')
                    
            except Exception as e:
                messages.error(request, f"Error saving test: {str(e)}")
        else:
            # Log form errors for debugging
            print("Form errors:", form.errors)
            messages.error(request, "Please correct the errors below")
    else:
        form = DoctorLabTestSuggestionForm()

    return render(request, 'appointments/suggest_lab_test.html', {
        'form': form,
        'patient': patient,
        'step': 1
    })
    
@login_required
def patient_lab_tests(request):
    """Show all lab tests for patient with pending actions"""
    if not hasattr(request.user, 'patientprofile'):
        messages.warning(request, "Access denied: Patient profile required.")
        return redirect('home')

    patient = request.user.patientprofile
    all_tests = LabTest.objects.filter(patient=patient).order_by('-created_at')
    
    # Include 'Sent to Lab' in pending tests
    pending_tests = all_tests.filter(status__in=['Suggested', 'Details Pending', 'Sent to Lab'])
    completed_tests = all_tests.filter(status='Completed')

    return render(request, 'appointments/patient_lab_tests.html', {
        'pending_tests': pending_tests,
        'completed_tests': completed_tests,
        'tests': all_tests  # Changed from 'all_tests' to 'tests' to match your template
    })


@login_required
def upload_lab_report(request, test_id):
    """Upload test results (without lab staff check)"""

    lab_test = get_object_or_404(LabTest, id=test_id, status='Sent to Lab')

    if request.method == 'POST':
        form = LabReportUploadForm(request.POST, request.FILES, instance=lab_test)
        if form.is_valid():
            lab_test = form.save(commit=False)
            lab_test.status = 'Completed'
            lab_test.completed_at = timezone.now()
            lab_test.save()

            # Notify both patient and doctor
            Notification.objects.create(
                recipient=lab_test.patient.user,
                message=f"Your lab report for {lab_test.test_name} is now available."
            )
            Notification.objects.create(
                recipient=lab_test.doctor.user,
                message=f"Lab results for {lab_test.patient.user.get_full_name()}'s {lab_test.test_name} test are available."
            )

            messages.success(request, "Lab report uploaded successfully!")
            return redirect('appointments:patient_lab_tests')  # or wherever you want to redirect

    else:
        form = LabReportUploadForm(instance=lab_test)

    return render(request, 'appointments/upload_lab_report.html', {
        'form': form,
        'test': lab_test
    })

@login_required
def doctor_patients_list(request):
    doctor = request.user.doctorprofile
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient__user')

    # Create a set to track seen patient IDs
    seen_patient_ids = set()
    unique_patients = []

    for appointment in appointments:
        patient = appointment.patient
        if patient.id not in seen_patient_ids:
            seen_patient_ids.add(patient.id)
            unique_patients.append(patient)

    return render(request, 'appointments/doctor_patients_list.html', {
        'patients': unique_patients
    })



@login_required
def patient_detail(request, patient_id):
    doctor = request.user.doctorprofile
    patient = get_object_or_404(PatientProfile, id=patient_id)

    # Get all appointments between this doctor and patient
    appointments = Appointment.objects.filter(
        doctor=doctor,
        patient=patient
    ).order_by('date')

    # Get all uploaded lab reports for this patient
    lab_reports = LabTest.objects.filter(
        patient=patient,
        report_file__isnull=False
    ).order_by('-created_at')

    # Calculate age
    if patient.date_of_birth:
        today = date.today()
        age = today.year - patient.date_of_birth.year - (
            (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
        )
    else:
        age = "N/A"

    return render(request, 'appointments/patient_detail.html', {
        'patient': patient,
        'appointments': appointments,
        'lab_reports': lab_reports,  # ✅ Add lab_reports to context
        'age': age  
    })
    
@login_required
def upload_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Only allow doctor to upload for their own appointments
    if request.user != appointment.doctor.user:
        raise PermissionDenied("You are not authorized to upload prescription for this appointment.")

    if request.method == 'POST' and request.FILES.get('prescription'):
        prescription_file = request.FILES['prescription']
        appointment.prescription = prescription_file
        appointment.save()
        messages.success(request, "Prescription uploaded successfully.")
    else:
        messages.error(request, "Please select a valid file to upload.")

    return redirect('appointments:patient_detail', patient_id=appointment.patient.id)


@login_required
def complete_lab_details(request, test_id):
    """Patient completes lab details (step 2)"""
    try:
        lab_test = LabTest.objects.get(
            id=test_id,
            patient=request.user.patientprofile,
            status__in=['Suggested', 'Details Pending']
        )
    except LabTest.DoesNotExist:
        messages.error(request, "Test not found or not available for completion")
        return redirect('appointments:patient_lab_tests')

    if request.method == 'POST':
        form = PatientLabDetailsForm(request.POST, instance=lab_test)
        if form.is_valid():
            try:
                with transaction.atomic():
                    lab_test = form.save(commit=False)
                    lab_test.status = 'Sent to Lab'
                    lab_test.is_completed_by_patient = True
                    lab_test.save()
                    form.save_m2m()

                    # Create notification with error handling
                    try:
                        Notification.objects.create(
                            recipient=lab_test.doctor.user,
                            message=f"Patient {lab_test.patient.user.get_full_name()} has completed details for {lab_test.test_name}",
                            notification_type='lab_test_submitted'
                        )
                    except Exception as e:
                        logger.error(f"Failed to create notification: {str(e)}")
                        # Continue even if notification fails

                    messages.success(request, "Lab details submitted successfully! The lab will contact you soon.")
                    return redirect('appointments:patient_lab_tests')
                    
            except Exception as e:
                messages.error(request, "An error occurred while saving your details. Please try again.")
                logger.error(f"Error completing lab details: {str(e)}")
    else:
        form = PatientLabDetailsForm(instance=lab_test)

    context = {
        'form': form,
        'test': lab_test,
        'step': 2,
        'page_title': f"Complete Details: {lab_test.test_name}"
    }
    return render(request, 'appointments/complete_lab_details.html', context)

@login_required
def patient_appointment_list(request):
    patient = request.user.patientprofile
    appointments = Appointment.objects.filter(patient=patient).prefetch_related('prescriptions', 'doctor__user')
    return render(request, 'appointments/patient_appointment_list.html', {
        'appointments': appointments,
    })
