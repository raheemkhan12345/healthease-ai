from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DoctorProfile, PatientProfile, TimeSlot, LoginLog, LabProfile


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_active', 'is_staff')
    list_filter = ('user_type', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Role', {'fields': ('user_type',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'hospital', 'experience')
    list_filter = ('specialization', 'hospital')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'address')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_booked')
    list_filter = ('date', 'is_booked')
    search_fields = ('doctor__user__username', 'doctor__user__first_name', 'doctor__user__last_name')


class LoginLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time', 'ip_address')
    list_filter = ('login_time',)
    search_fields = ('user__username', 'ip_address', 'user_agent')


class LabProfileAdmin(admin.ModelAdmin):
    list_display = ('lab_name', 'user')
    search_fields = ('lab_name', 'user__username')


admin.site.register(User, CustomUserAdmin)
admin.site.register(DoctorProfile, DoctorProfileAdmin)
admin.site.register(PatientProfile, PatientProfileAdmin)
admin.site.register(TimeSlot, TimeSlotAdmin)
admin.site.register(LoginLog, LoginLogAdmin)
admin.site.register(LabProfile, LabProfileAdmin)
