from rest_framework.serializers import ModelSerializer
from drchrono.models import Doctor, Patient, Appointment


class LimitedModelSerializer(ModelSerializer):

    def to_representation(self, instance):
        """
        raises NotImplemented. This app does NOT push models outbound; any editing required is done directly through
        the API.
        """
        raise NotImplemented("This is a one-way serializer; API -> Model only")

    def to_internal_value(self, data):
        """
        Discards all data that isn't specified in self.fields, since we don't care to store it.
        """
        internal_data = {k: data[k] for k in self.fields}
        return internal_data


class PatientSerializer(LimitedModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'first_name', 'last_name', 'date_of_birth')
        depth = 1


class DoctorSerializer(LimitedModelSerializer):
    class Meta:
        model = Doctor
        fields = ('id', 'first_name', 'last_name')
        depth = 1


class AppointmentSerializer(LimitedModelSerializer):
    class Meta:
        model = Appointment
        fields = ('id', 'patient', 'doctor', 'status', 'scheduled_time', 'duration')
        depth = 1

    # We push the update/create responsibility to the API resource layer so the serializers don't need to know how to
    # connect to the API at all; instead they just handle the data
    def create(self, validated_data):
        """
        Only allows appointment creation if the referenced Doctor and Patient are already in the database

        Raises Doctor.DoesNotExist or Patient.DoesNotExist when they aren't.
        """
        doctor_id = validated_data.pop('doctor')
        validated_data['doctor'] = Doctor.objects.get(id=doctor_id)
        patient_id = validated_data.pop('patient')
        validated_data['patient'] = Patient.objects.get(id=patient_id)
        Appointment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Only allows appointment updates if the referenced Doctor and Patient are already in the database.

        Raises Doctor.DoesNotExist or Patient.DoesNotExist when they aren't.
        """
        doctor_id = validated_data.pop('doctor')
        validated_data['doctor'] = Doctor.objects.get(id=doctor_id)
        patient_id = validated_data.pop('patient')
        validated_data['patient'] = Patient.objects.get(id=patient_id)
        # Only works because the model is so simple.
        for field_name in self.fields:
            setattr(instance, field_name, validated_data[field_name])
        instance.save()