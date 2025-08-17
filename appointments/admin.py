from django.contrib import admin
from .models import Appointment

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'patient', 'date', 'start_time', 'status')
    search_fields = ('doctor__user__username', 'patient__user__username')
    list_filter = ('status', 'date')

admin.site.register(Appointment, AppointmentAdmin)
