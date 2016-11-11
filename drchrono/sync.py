# Sync the external API information to the local django-based cache
from drchrono.endpoints import DoctorEndpoint
from drchrono.models import Doctor
from drchrono.serializers import DoctorSerializer

def sync_model(model_klas, serializer_klass, endpoint_klass)

class ModelSync(object):
    endpoint = None
    serializer = None
    model = None

    def __call__(self, *args, **kwargs):
        endpoint = self.endpoint()
        for doctor_data in endpoint.list():
            serializer = self.serializer(data=doctor_data)
            if serializer.is_valid():
                try:
                    model = self.model.objects.get(serializer.validated_data['id'])
                    serializer.update(model, serializer.validated_data)
                except Doctor.DoesNotExist:
                    serializer.create(serializer.validated_data)


class DoctorSync(ModelSync):
    endpoint = DoctorEndpoint
    serializer = DoctorSerializer
    model = Doctor