from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'appointments'
urlpatterns = [
    
     path('about/', views.about, name='about'),
     path('services/', views.services, name='services'),
     path('contact/', views.contact, name='contact'),

    path('login/doctor/', views.doctor_login, name='doctor_login'),
    path('login/patient/', views.patient_login, name='patient_login'),
    path('signup/doctor/', views.doctor_signup, name='doctor_signup'),
    path('signup/patient/', views.patient_signup, name='patient_signup'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard/Profile URLs
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),
    path('patient/profile/', views.patient_profile, name='patient_profile'),

    path('doctor/signup/', views.doctor_signup, name='doctor_signup'),  # Make sure this exists
    path('signup/patient/', views.patient_signup, name='patient_signup'),
    
    path('doctors/', views.doctor_search, name='doctor_search'),
     path('doctors/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('doctors/<int:doctor_id>/book/', views.book_appointment, name='book_appointment'),
    path('appointments/<int:appointment_id>/confirm/', views.appointment_confirmation, name='appointment_confirmation'),
    path('appointments/<int:appointment_id>/video/', views.video_consultation, name='video_consultation'),
    path('confirmation/<int:appointment_id>/', views.appointment_confirmation, name='appointment_confirmation'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)