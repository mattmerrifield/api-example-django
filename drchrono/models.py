from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from localflavor.us.models import USSocialSecurityNumberField
import datetime as dt


# These models know very little about how they are created; only a bit of data that we want to cache locally, and how
# they're related to each other.

class Patient(models.Model):
    # These values are never edited locally; only in response to information from the server
    # We cache the minimum number of fields to provide useful info to the doctor.
    first_name = models.CharField(editable=False, max_length=255, null=True)
    last_name = models.CharField(editable=False, max_length=255, null=True)
    date_of_birth = models.DateField(editable=False, null=True)
    social_security_number = USSocialSecurityNumberField(editable=False, null=True)

    def __str__(self):
        return "{self.first_name} {self.last_name}".format(self=self)


class Doctor(models.Model):
    # These values are never edited locally; only in response to information from the server
    # We cache the minimum number of fields to provide useful info to the doctor.
    first_name = models.CharField(max_length=255, editable=False)
    last_name = models.CharField(max_length=255, editable=False)

    def __str__(self):
        return "Dr. {self.last_name}".format(self=self)


class AppointmentManager(models.Manager):
    def today(self):
        midnight = now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = midnight + dt.timedelta(days=1)
        return self.filter(
            scheduled_time__gte=midnight,
            scheduled_time__lte=tomorrow,
        ).order_by('scheduled_time')


class Appointment(models.Model):
    """
    An appointment to see the doctor.
    """
    # These values are never changed locally; only in response to information from the server
    id = models.CharField(primary_key=True, max_length=255)  # Appointments are keyed with a string, for better or worse
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, editable=False, null=True)  # Breaks have a null patient field
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, editable=False)  # Must have a doctor
    status = models.CharField(max_length=255, editable=False, null=True)
    scheduled_time = models.DateTimeField(default=now, editable=False)
    duration = models.IntegerField(editable=False)

    # These values you can edit locally, and are not transmitted to the server.
    checkin_time = models.DateTimeField(null=True)
    seen_time = models.DateTimeField(null=True)
    time_waiting = models.IntegerField(null=True)

    # custom manager with a today() method
    objects = AppointmentManager()

    def __init__(self, *args, **kwargs):
        super(Appointment, self).__init__(*args, **kwargs)
        # Set the time_waiting on initialization for people who are sitting in the office, so we can view their
        # time waiting live. This will not be saved; .save() overwrites it with its own logic
        if self.checkin_time and not self.seen_time and self.status == 'Arrived':
            self.time_waiting = now() - self.checkin_time

    def __str__(self):
        patient = self.patient or "Break"
        return "{self.scheduled_time} {patient} with {self.doctor} for {self.duration} minutes".format(
            self=self, patient=patient)

    def check_in(self):
        self.status = 'Waiting'
        self.checkin_time = now()
        self.seen_time = None
        self.save()

    def start_consult(self):
        self.status = 'In Session'
        self.seen_time = now()
        self.save()

    def finish_consut(self):
        self.status = 'Complete'
        self.save()


    def save(self, *args, **kwargs):
        """
        Return the time spent waiting for patients who have checked in.

        Return None for patients who haven't checked in.
        :return:
        """
        # For simplicity, people only get this metric after they're seen.
        if self.checkin_time and self.seen_time:
            duration_waiting = self.seen_time - self.checkin_time
            self.time_waiting = duration_waiting.total_seconds()/60
        else:
            self.time_waiting = None
        super(Appointment, self).save(*args, **kwargs)


