from django.contrib import admin

from drchrono.models import Patient, Appointment, Doctor


class PatientAdmin(admin.ModelAdmin):
    pass  # bone stock for now


class DoctorAdmin(admin.ModelAdmin):
    pass


class AppointmentAdmin(admin.ModelAdmin):
    """
    Primary admin interface to view *all* appointments.
    """
    list_display = ['patient', 'status', 'scheduled_time', 'checkin_time', 'time_waiting']


admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Appointment, AppointmentAdmin)
