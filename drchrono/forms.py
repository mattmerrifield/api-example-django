from django import forms
from django.forms import widgets
from localflavor.us.forms import USSocialSecurityNumberField, USPhoneNumberField

from drchrono.models import Patient, Appointment, Doctor


class PatientWhoamiForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    date_of_birth = forms.DateField(required=False, widget=widgets.DateInput)
    social_security_number = USSocialSecurityNumberField(required=False)

    def get_patient(self):
        data = {f: self.cleaned_data[f] for f in self.cleaned_data if self.cleaned_data[f]}
        # All form fields should be patient attributes, so we can construct filters this cheezy way.
        filters = {"{}".format(f): data[f] for f in data}
        return Patient.objects.get(**filters)

    def is_valid(self):
        originall_valid = super(PatientWhoamiForm, self).is_valid()
        first_last_dob = ['first_name', 'last_name', 'date_of_birth']
        if not(all(self.cleaned_data[k] for k in first_last_dob) or self.cleaned_data['social_security_number']):
            self.add_error(None, 'Provide either SSN, or first/last/DOB')
            return False
        else:
            try:
                self.get_patient()
                return originall_valid
            except Patient.DoesNotExist:
                self.add_error(None, "You are not yet registered, or you made a typo. \nPlease try again, or see the receptionist.")
                return False
            except Patient.MultipleObjectsReturned:
                self.add_error(None, "You have more than one account registered. Please see the receptionist.")
                return False


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
    appointment = forms.ModelChoiceField(
        queryset=Appointment.objects.all(),
        widget=widgets.RadioSelect,
        empty_label=None,
    )

    def __init__(self, patient='', **kwargs):
        super(AppointmentChoiceForm, self).__init__(**kwargs)
        self.patient = patient
        self.fields['appointment'].queryset = Appointment.objects.today().filter(patient=self.patient)
