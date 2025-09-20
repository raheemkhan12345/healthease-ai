from django.contrib import admin
from .models import Appointment, LabTest, Notification, Prescription


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'patient', 'date', 'start_time', 'end_time', 'transaction_id', 'status')
    list_filter = ('status', 'date')
    search_fields = ('doctor__user__username', 'patient__user__username', 'transaction_id')


class LabTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_name', 'doctor', 'patient', 'lab', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('test_name', 'doctor__user__username', 'patient__user__username', 'lab__lab_name')


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'message')


class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('appointment__doctor__user__username', 'appointment__patient__user__username')


admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(LabTest, LabTestAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Prescription, PrescriptionAdmin)
