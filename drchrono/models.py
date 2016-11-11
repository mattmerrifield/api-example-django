from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Patient(models.Model):
    # These values are never edited locally; only in response to information from the server
    # We cache the minimum number of fields to provide useful info to the doctor.
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()

    # We store the last time we did a refresh from the API, so we can decide when to do another one.
    # refresh_time = models.DateTimeField()

    def __str__(self):
        return "{self.first_name} {self.last_name}".format(self=self)


class Doctor(models.Model):
    # These values are never edited locally; only in response to information from the server
    # We cache the minimum number of fields to provide useful info to the doctor.
    id = models.IntegerField(editable=False)
    first_name = models.CharField(max_length=255, editable=False)
    last_name = models.CharField(max_length=255, editable=False)


class Appointment(models.Model):
    """
    An appointment to see the doctor.
    """
    # These values are never changed locally; only in response to information from the server
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, editable=False, null=True)  # Breaks have a null patient field
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, editable=False)
    status = models.CharField(max_length=255, editable=False)
    scheduled_time = models.DateTimeField(default=now, editable=False)
    duration = models.IntegerField(editable=False)

    # These values you can edit locally, and are not transmitted to the server.
    checkin_time = models.DateTimeField(null=True)
    seen_time = models.DateTimeField(null=True)
