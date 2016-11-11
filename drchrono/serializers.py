from rest_framework.serializers import ModelSerializer
from drchrono.models import Doctor, Patient, Appointment


class PatientSerialier(ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'first_name', 'last_name', 'date_of_birth')
        depth = 1


class DoctorSerializer(ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('id', 'first_name', 'last_name')
        depth = 1


class AppointmentSerializer(ModelSerializer):
    class Meta:
        model = Appointment
        fields = ('id', 'patient', 'doctor', 'status', 'scheduled_time', 'duration')
        depth = 1

    def create(self, validated_data):
        """
        Only allow creation if the referenced Doctor and Patient are already in the database

        Might raise Doctor.DoesNotExist or Patient.DoesNotExist; The view that uses this serializer is responsible for
        Handling (or preventing) these cases.
        """
        # We push this responsibility to the API resource layer so the serializers don't need to know how to
        # connect to the API at all; instead they just handle the data
        #
        # This will raise Doctor.DoesNotExist
        doctor_id = validated_data.pop('doctor')
        validated_data['doctor'] = Doctor.objects.get(id=doctor_id)
        # This will raise Patient.DoesNotExist
        patient_id = validated_data.pop('patient')
        validated_data['patient'] = Patient.objects.get(id=patient_id)
        # Only works if everything is already hunky-dory
        Appointment.objects.create(**validated_data)
