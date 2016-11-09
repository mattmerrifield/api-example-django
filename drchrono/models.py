from django.db import models
from localflavor.us.forms import USSocialSecurityNumberField


# Create your models here.
class Patient(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    social_security_number = USSocialSecurityNumberField()
    dob = models.DateField()


APPOINTMENT_STATUSES = [
    ('walk-in', 'Walk-in'),
    ('scheduled', 'Scheduled'),
    ('arrived', 'Arrived'),
    ('complete', 'Compete'),
    ('canceled', 'Canceled')
]


class Appointment(models.Model):
    status = models.CharField(choices=APPOINTMENT_STATUSES, default=APPOINTMENT_STATUSES[0][0], max_length=255)
    time_scheduled = models.DateTimeField(null=True)  # null to allow walk-ins
    time_checked_in = models.DateTimeField(null=True)
    time_seen = models.DateTimeField(null=True)
    notes = models.TextField(default="")