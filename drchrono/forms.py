from django import forms
from django.utils.timezone import now
from localflavor.us.forms import USSocialSecurityNumberField, USPhoneNumberField

from drchrono.models import Patient, Appointment, Doctor


class PatientWhoamiForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    date_of_birth = forms.DateField()
    social_security_number = USSocialSecurityNumberField(required=False)


class PatientInfoForm(forms.Form):
    # This set of fields needs way more validation and care than I'm currently giving it
    # We're going to feed these results directly to the API; we should make sure the API won't choke on what we give it
    first_name = forms.CharField()
    middle_name = forms.CharField()
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    last_name = forms.CharField()
    date_of_birth = forms.DateField(required=False)
    social_security_number = USSocialSecurityNumberField(required=False)
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all())
    address = forms.CharField(required=False)
    city = forms.CharField(required=False)
    cell_phone = USPhoneNumberField(required=False)
    # TODO:
    # custom demographics fields are dynamically constructed; this is tricky with django forms


class AppointmentChoiceForm(forms.Form):
    appointment = forms.ModelChoiceField(queryset=Appointment.objects.all())

    def __init__(self, patient=None, start=None, end=None, **kwargs):
        super(AppointmentChoiceForm, self).__init__(**kwargs)
        self.patient = patient  # Template breaks if patient=None
        if patient:
            self.fields['appointment'].queryset = self.fields['appointment'].queryset.filter(patient=patient)
        if start:
            self.fields['appointment'].queryset = self.fields['appointment'].queryset.filter(scheduled_time__gte=start)
        if end:
            self.fields['appointment'].queryset = self.fields['appointment'].queryset.filter(scheduled_time__lte=end)
