from django import forms
from localflavor.us.forms import USSocialSecurityNumberField

class CheckInForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    date_of_birth = forms.DateField()
    social_security_number = USSocialSecurityNumberField(required=False)