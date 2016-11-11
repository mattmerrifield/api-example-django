# Sync the external API information to the local django-based cache
from django.utils.timezone import now
import datetime as dt
from drchrono.endpoints import DoctorEndpoint, AppointmentEndpoint, PatientEndpoint
from drchrono.models import Doctor, Appointment, Patient
from drchrono.serializers import DoctorSerializer, AppointmentSerializer, PatientSerializer


class ModelSync(object):
    """
    Syncs all data from API -> Model using a Serializer.
    """
    # Written in a Java-thread kinda way, in case we want to go that route.
    # however, threads on python are kind of terrible, so I'd rather not.
    endpoint = None
    serializer = None
    model = None

    def run(self, *args, **kwargs):
        self.sync()

    def get_list_kwargs(self):
        """
        returns a dictionary of kwargs to feed to the endpoint.list(**kwargs) method
        """
        return {}

    def sync(self):
        endpoint = self.endpoint()
        for doctor_data in endpoint.list(**self.get_list_kwargs()):
            serializer = self.serializer(data=doctor_data)
            if serializer.is_valid():
                try:
                    model = self.model.objects.get(id=serializer.validated_data['id'])
                    serializer.update(model, serializer.validated_data)
                except self.model.DoesNotExist:
                    serializer.create(serializer.validated_data)


class DoctorSync(ModelSync):
    endpoint = DoctorEndpoint
    serializer = DoctorSerializer
    model = Doctor


class AppointmentSync(ModelSync):
    endpoint = AppointmentEndpoint
    serializer = AppointmentSerializer
    model = Appointment

    def get_list_kwargs(self):
        return {'start': now() - dt.timedelta(90), 'end': now() + dt.timedelta(90)}


class PatientSync(ModelSync):
    endpoint = PatientEndpoint
    serializer = PatientSerializer
    model = Patient


def sync_all():
    DoctorSync().run()
    PatientSync().run()
    AppointmentSync().run()


