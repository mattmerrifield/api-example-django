from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from localflavor.us.forms import USSocialSecurityNumberField
import datetime as dt


class Doctor(User):
    """
    Proxy model for a Doctor, containing extension logic to the original Django framework's auth module. Doctors get
    admin access to the kiosk system, and can view the built-in admin panels.
    """
    class Meta:
        proxy = True


class Patient(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    social_security_number = USSocialSecurityNumberField()
    dob = models.DateField()

    def __str__(self):
        return "{self.first_name} {self.last_name}".format(self=self)

# Reference these constants elsewhere in the codebase
# instead of hard-coding the string; we might change nomenclature
WALK_IN = 'walk-in'
SCHEDULED = 'scheduled'
ARRIVED = 'arrived'
NORMAL = 'normal'

APPOINTMENT_TYPES = [
    (WALK_IN, 'Walk-in'),
    (NORMAL, 'Normal')
]

PATIENT_STATUS = [
    (SCHEDULED, 'Scheduled'),
    (ARRIVED, 'Arrived'),
    ('complete', 'Compete'),
    ('canceled', 'Canceled')
]


class Appointment(models.Model):
    """
    An appointment to see the doctor.
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)  # Please don't delete doctors! Set them inactive instead
    type = models.CharField(choices=APPOINTMENT_TYPES, default=NORMAL, max_length=255)
    status = models.CharField(choices=PATIENT_STATUS, default=SCHEDULED, max_length=255)
    time_scheduled = models.DateTimeField(default=now)  # Walk-ins will be scheduled for now, with status arrived.
    time_checked_in = models.DateTimeField(null=True)
    time_seen = models.DateTimeField(null=True)
    notes = models.TextField(default="")

    # Making this a property right now, but a case could be made to turn it into an actual database field, calculated
    # and set by the .save() method (and not user-editable)
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


class TodaysAppointmentManager(models.Manager):
    def get_queryset(self):
        qs = super(TodaysAppointmentManager, self).get_queryset()
        morning = now().replace(hour=6, minute=0, second=0, microsecond=0)
        evening = morning + dt.timedelta(days=1)  # Possible DST bug?
        return qs.filter(time_scheduled__gt=morning, time_scheduled=evening)


class TodaysAppointments(Appointment):
    class Meta:
        proxy = True
    objects = TodaysAppointmentManager()


class CurrentlyWaitingManager(models.Manager):
    def get_queryset(self):
        qs = super(CurrentlyWaitingManager, self).get_queryset()
        return qs.filter(status=ARRIVED)


class CurrentlyWaiting(Appointment):
    class Meta:
        proxy = True
    objects = CurrentlyWaitingManager()