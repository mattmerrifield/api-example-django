from django.contrib import admin

from drchrono.models import Patient, Appointment


class PatientAdmin(admin.ModelAdmin):
    pass  # bone stock for now


class AppointmentAdmin(admin.ModelAdmin):
    pass  # bone stock for now


admin.site.register(Patient, PatientAdmin)
admin.site.register(Appointment, AppointmentAdmin)
