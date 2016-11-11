from django import forms
from django.utils.timezone import now
from localflavor.us.forms import USSocialSecurityNumberField

from drchrono.models import Patient, Appointment


class PatientWhoamiForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    date_of_birth = forms.DateField()
    social_security_number = USSocialSecurityNumberField(required=False)


class AppointmentChoiceForm(forms.Form):
    appointment = forms.ModelChoiceField(queryset=Appointment.objects.all())

    def __init__(self, patient=None, start=None, end=None, **kwargs):
        super(AppointmentChoiceForm, self).__init__(**kwargs)
        if patient:
            self.appointment.queryset = self.appointment.queryset.filter(patient=patient)
        if start:
            self.appointment.queryset = self.appointment.queryset.filter(scheduled_time__gte=start)
        if end:
            self.appointment.queryset = self.appointment.queryset.filter(scheduled_time__lte=end)
