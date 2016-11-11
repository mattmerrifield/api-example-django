# from django.contrib import admin
#
# from drchrono.models import Patient, Appointment, Doctor, TodaysAppointments, CurrentlyWaiting
#
#
# class PatientAdmin(admin.ModelAdmin):
#     pass  # bone stock for now
#
#
# class DoctorAdmin(admin.ModelAdmin):
#     pass
#
#
# class AppointmentAdmin(admin.ModelAdmin):
#     """
#     Primary admin interface to view *all* appointments.
#     """
#     list_display = ['patient', 'type', 'status', 'time_scheduled', 'time_checked_in', 'time_waiting']
#
#
# admin.site.register(Doctor, DoctorAdmin)
# admin.site.register(Patient, PatientAdmin)
# admin.site.register(Appointment, AppointmentAdmin)
# admin.site.register(TodaysAppointments, AppointmentAdmin)
# # admin.site.register(CurrentlyWaiting, AppointmentAdmin)
