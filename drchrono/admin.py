from django.contrib import admin

from drchrono.models import Patient, Appointment


class PatientAdmin(admin.ModelAdmin):
    pass  # bone stock for now


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'time_scheduled', 'time_checked_in', 'time_waiting']

admin.site.register(Patient, PatientAdmin)
admin.site.register(Appointment, AppointmentAdmin)
