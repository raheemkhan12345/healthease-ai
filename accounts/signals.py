from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import DoctorProfile, PatientProfile
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
from .models import LoginLog


User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_doctor:
            DoctorProfile.objects.create(user=instance)
        elif instance.is_patient:
            PatientProfile.objects.create(
                user=instance,
                date_of_birth=instance.date_of_birth if hasattr(instance, 'date_of_birth') else None
            )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'doctorprofile'):
        instance.doctorprofile.save(update_fields=[
            'specialization',
            'hospital',
            'experience'
        ])
    elif hasattr(instance, 'patientprofile'):
        instance.patientprofile.save(update_fields=[
            'date_of_birth'
            # Add other patient profile fields here as needed
        ])
        
        @receiver(user_logged_in)
        def record_login(sender, request, user, **kwargs):
         LoginLog.objects.create(
        user=user,
        session_key=request.session.session_key
    )

    @receiver(user_logged_out)
    def record_logout(sender, request, user, **kwargs):
     LoginLog.objects.filter(
        user=user,
        session_key=request.session.session_key,
        logout_time__isnull=True
    ).update(logout_time=timezone.now())