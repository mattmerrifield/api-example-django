from django.db import models
from django.utils.timezone import now
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

    @property
    def time_waiting(self):
        """
        Return the time spent waiting for patients who have checked in.

        Return None for patients who haven't checked in.
        :return:
        """
        # assumes time_seen is either never in the future, or perfectly prophetic of how long a person *will* have
        # been waiting.
        if not self.time_checked_in:
            return None
        elif self.time_seen:
            return self.time_seen - self.time_checked_in
        else:
            return now() - self.time_checked_in