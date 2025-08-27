from venv import logger
from datetime import datetime, time, timedelta, date

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import make_aware, localtime, now
from django.views.decorators.http import require_GET
from accounts.models import User, DoctorProfile, PatientProfile
from .forms import (
    AppointmentForm,
    DoctorLoginForm,
    DoctorSearchForm,
    DoctorSignUpForm,
    LabReportUploadForm,
    LabTestForm as DoctorLabTestSuggestionForm,
    PatientLabDetailsForm,
    PatientLoginForm,
    PatientSignUpForm,
)
from .models import Appointment, LabTest, Notification

# ----------------------
# Static pages / dashboards
# ----------------------
def home(request):
    form = DoctorSearchForm()
    context = {
        'form': form,
        'specializations': DoctorProfile.SPECIALIZATION_CHOICES,
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def contact(request):
    return render(request, 'contact.html')

def landing_page(request):
    return render(request, 'landing.urls')

def doctor_signup(request):
    return render(request, 'doctor_signup.urls')

def patient_signup_page(request):  # renamed to avoid colliding with the real signup view below
    return render(request, 'patient_signup.urls')

def doctor_dashboard(request):
    return render(request, 'accounts/doctor_dashboard.html')

def patient_dashboard(request):
    return render(request, 'accounts/patient_dashboard.html')

def doctor_profile(request):
    return render(request, 'doctor_profile')

def patient_profile(request):
    return render(request, 'patient_profile')

def chatbot_view(request):
    return render(request, 'chatbot.html')


# ----------------------
# Auth (login/logout/signup)
# ----------------------
def doctor_login(request):
    if request.user.is_authenticated and hasattr(request.user, 'doctorprofile'):
        return redirect('doctor_dashboard')

    if request.method == 'POST':
        form = DoctorLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and hasattr(user, 'doctorprofile'):
                login(request, user)
                return redirect('doctor_dashboard')
            else:
                messages.error(request, 'Invalid doctor credentials')
    else:
        form = DoctorLoginForm()
    return render(request, 'auth/doctor_login.html', {'form': form})

def patient_login(request):
    if request.user.is_authenticated and hasattr(request.user, 'patientprofile'):
        return redirect('patient_dashboard')

    if request.method == 'POST':
        form = PatientLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and hasattr(user, 'patientprofile'):
                login(request, user)
                return redirect('patient_dashboard')
            else:
                messages.error(request, 'Invalid patient credentials')
    else:
        form = PatientLoginForm()
    return render(request, 'auth/patient_login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

# Real patient signup (kept as in your original)
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


# ----------------------
# Search doctors
# ----------------------
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

        # 🔹 Filter lagana
        filters = Q()

        if specialization:   # agar specialization select kiya ho
            filters &= Q(specialization=specialization)

        if location:   # agar location select kiya ho
            filters &= Q(hospital__icontains=location)

        if query:   # agar name search kiya ho
            filters &= (
                Q(user__username__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
            )

        if filters:  # agar koi filter apply hua ho
            doctors = doctors.filter(filters)

    # order by experience
    doctors = doctors.order_by('-experience')

    # pagination
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


# ----------------------
# Booking flows
# ----------------------

def generate_time_slots(start, end, interval=30):
    """Generate slots between start & end times with given interval in minutes."""
    slots = []
    current = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)
    while current <= end_dt:
        slots.append(current.time())
        current += timedelta(minutes=interval)
    return slots


def generate_time_slots(start, end, interval_minutes=30):
    """Generate 30 min time slots between start & end"""
    slots = []
    current = datetime.combine(datetime.today(), start)
    end_time = datetime.combine(datetime.today(), end)

    while current <= end_time:
        slots.append(current.time())
        current += timedelta(minutes=interval_minutes)

    return slots


@login_required
def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    slots = generate_time_slots(time(9, 0), time(20, 0))

    if request.method == "POST":
        form = AppointmentForm(request.POST, doctor=doctor)
        active_tab = "book"

        if form.is_valid():
            patient = request.user.patientprofile
            appointment = form.save(commit=False)
            appointment.doctor = doctor
            appointment.patient = patient
            appointment.status = "pending"
            # end_time auto calculate
            start_time = datetime.strptime(form.cleaned_data["start_time"], "%H:%M").time()
            appointment.start_time = start_time
            appointment.end_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=30)).time()
            appointment.save()

            messages.success(request, "✅ Appointment booked successfully.")
            return redirect("appointments:appointment_confirmation", appointment.id)
    else:
        form = AppointmentForm(doctor=doctor)
        active_tab = "about"

    return render(request, "appointments/doctor_detail.html", {
        "doctor": doctor,
        "form": form,
        "active_tab": active_tab,
    })



@login_required
def appointment_confirmation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'appointments/appointment_confirmation.html', {'appointment': appointment})

def home(request):
    # Normal specializations for search dropdown
    specializations = [
        ('Cardiologist', 'Cardiologist'),
        ('Dermatologist', 'Dermatologist'),
        ('Neurologist', 'Neurologist'),
        ('Orthopedic', 'Orthopedic'),
        ('Pediatrician', 'Pediatrician'),
        ('Gynecologist', 'Gynecologist'),
       
    ]

    # Specialist section with icons (FontAwesome icons)
    specializations_with_icons = [
        ('Cardiologist', 'Cardiologist', 'fa-heart-pulse'),
        ('Dermatologist', 'Dermatologist', 'fa-user-md'),
        ('Neurologist', 'Neurologist', 'fa-brain'),
        ('Orthopedic', 'Orthopedic', 'fa-bone'),
        ('Pediatrician', 'Pediatrician', 'fa-child'),
        ('Gynecologist', 'Gynecologist', 'fa-venus'),
        ('lab', 'Lab Reports', 'fa-vials'),
    ]

    return render(request, "home.html", {
        "specializations": specializations,
        "specializations_with_icons": specializations_with_icons,
    })


@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    patient = request.user.patientprofile  

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            # ✅ Check overlapping appointments for same doctor & date
            conflict = Appointment.objects.filter(
                doctor=doctor,
                date=date,
                status__in=["pending", "confirmed", "approved"]
            ).filter(
                Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
            ).exists()

            if conflict:
                # ❌ Do NOT auto-assign next day, just show message
                messages.error(
                    request,
                    f"❌ The slot {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')} "
                    f"on {date.strftime('%B %d, %Y')} is already booked with Dr. {doctor.user.get_full_name()}. "
                    f"👉 Please choose another time or try booking the same slot on the next day."
                )
                return render(request, "appointments/doctor_detail.html", {
                    "doctor": doctor,
                    "form": form
                })

            # ✅ Save appointment if no conflict
            appointment = form.save(commit=False)
            appointment.doctor = doctor
            appointment.patient = patient
            appointment.status = "pending"
            appointment.save()

            messages.success(request, "✅ Your appointment has been booked and is waiting for doctor approval.")
            return redirect("accounts:patient_dashboard")
    else:
        form = AppointmentForm()

    return render(request, "appointments/doctor_detail.html", {"form": form, "doctor": doctor})

@login_required
def approve_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if not hasattr(request.user, 'doctorprofile') or request.user.doctorprofile != appointment.doctor:
        messages.error(request, "You are not authorized to approve this appointment.")
        return redirect('accounts:doctor_dashboard')

    if appointment.status in ['cancelled', 'completed']:
        messages.error(request, "You cannot approve a cancelled or completed appointment.")
        return redirect('accounts:doctor_dashboard')

    try:
        appointment.status = 'approved'
        appointment.full_clean()
        appointment.save()

        # Doctor ko message
        messages.success(request, "✅ Appointment approved successfully.")

        # Patient ke liye notification
        Notification.objects.create(
            recipient=appointment.patient.user,
            message=f"✅ Dr. {appointment.doctor.user.get_full_name() or appointment.doctor.user.username} has approved your appointment on {appointment.date} at {appointment.start_time}.",
            content_object=appointment
        )

    except ValidationError as e:
        msg = "; ".join(e.messages) if hasattr(e, 'messages') else str(e)
        messages.error(request, f"Approval failed: {msg}")

    return redirect('accounts:doctor_dashboard')



@login_required
def video_consultation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Only the appointment's doctor/patient or staff can access
    is_doctor = hasattr(request.user, 'doctorprofile') and appointment.doctor.user == request.user
    is_patient = hasattr(request.user, 'patientprofile') and appointment.patient.user == request.user
   

    if not (is_doctor or is_patient ):
        return render(request, 'appointments/access_denied.html')

    
    if appointment.status != 'approved':
        messages.error(request, "Consultation is not available until the appointment is approved by the doctor.")
      

    # ✅ Allow only within [start - 15, end + 15]
    if not appointment.can_join_consultation():
        start_local = localtime(appointment.get_start_datetime())
        end_local = localtime(appointment.get_end_datetime())
        messages.error(
            request,
            f"Video consultation is only accessible between "
            f"{(start_local - timedelta(minutes=Appointment.BUFFER_MINUTES)).strftime('%Y-%m-%d %H:%M')} and "
            f"{(end_local + timedelta(minutes=Appointment.BUFFER_MINUTES)).strftime('%Y-%m-%d %H:%M')}."
        )
        return redirect('appointments:appointment_confirmation', appointment.id)

    return render(request, 'appointments/video_consultation.html', {
        'appointment': appointment,
        'room_name': appointment.jitsi_room_name
    })


# ----------------------
# Misc (autocomplete, labs, patients list, etc.)
# ----------------------


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
    if not hasattr(request.user, 'patientprofile'):
        messages.warning(request, "Access denied: Patient profile required.")
        return redirect('home')

    patient = request.user.patientprofile
    all_tests = LabTest.objects.filter(patient=patient).order_by('-created_at')

    pending_tests = all_tests.filter(status__in=['Suggested', 'Details Pending', 'Sent to Lab'])
    completed_tests = all_tests.filter(status='Completed')

    return render(request, 'appointments/patient_lab_tests.html', {
        'pending_tests': pending_tests,
        'completed_tests': completed_tests,
        'tests': all_tests
    })


@login_required
def upload_lab_report(request, test_id):
    lab_test = get_object_or_404(LabTest, id=test_id, status='Sent to Lab')

    if request.method == 'POST':
        form = LabReportUploadForm(request.POST, request.FILES, instance=lab_test)
        if form.is_valid():
            lab_test = form.save(commit=False)
            lab_test.status = 'Completed'
            lab_test.completed_at = timezone.now()
            lab_test.save()

            Notification.objects.create(
                recipient=lab_test.patient.user,
                message=f"Your lab report for {lab_test.test_name} is now available."
            )
            Notification.objects.create(
                recipient=lab_test.doctor.user,
                message=f"Lab results for {lab_test.patient.user.get_full_name()}'s {lab_test.test_name} test are available."
            )

            messages.success(request, "Lab report uploaded successfully!")
            return redirect('appointments:patient_lab_tests')
    else:
        form = LabReportUploadForm(instance=lab_test)

    return render(request, 'appointments/upload_lab_report.html', {'form': form, 'test': lab_test})


@login_required
def doctor_patients_list(request):
    doctor = request.user.doctorprofile
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient__user')

    seen_patient_ids = set()
    unique_patients = []
    for appt in appointments:
        patient = appt.patient
        if patient.id not in seen_patient_ids:
            seen_patient_ids.add(patient.id)
            unique_patients.append(patient)

    return render(request, 'appointments/doctor_patients_list.html', {'patients': unique_patients})


@login_required
def patient_detail(request, patient_id):
    doctor = request.user.doctorprofile
    patient = get_object_or_404(PatientProfile, id=patient_id)

    appointments = Appointment.objects.filter(doctor=doctor, patient=patient).order_by('date')

    lab_reports = LabTest.objects.filter(patient=patient, report_file__isnull=False).order_by('-created_at')

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
        'lab_reports': lab_reports,
        'age': age
    })


@login_required
def upload_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.user != appointment.doctor.user:
        raise PermissionDenied("You are not authorized to upload prescription for this appointment.")

    if request.method == 'POST' and request.FILES.get('prescription'):
        appointment.prescription = request.FILES['prescription']
        appointment.save()
        messages.success(request, "Prescription uploaded successfully.")
    else:
        messages.error(request, "Please select a valid file to upload.")

    return redirect('appointments:patient_detail', patient_id=appointment.patient.id)


@login_required
def complete_lab_details(request, test_id):
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

                    try:
                        Notification.objects.create(
                            recipient=lab_test.doctor.user,
                            message=f"Patient {lab_test.patient.user.get_full_name()} has completed details for {lab_test.test_name}",
                        )
                    except Exception as e:
                        logger.error(f"Failed to create notification: {str(e)}")

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
    return render(request, 'appointments/patient_appointment_list.html', {'appointments': appointments})
