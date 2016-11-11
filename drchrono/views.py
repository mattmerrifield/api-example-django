from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.views import generic
from django.views.generic import TemplateView
from django.views.generic.list import ListView

from drchrono.endpoints import PatientEndpoint, AppointmentEndpoint
from drchrono.forms import PatientWhoamiForm, AppointmentChoiceForm, PatientInfoForm
from drchrono.models import Appointment, Patient
from drchrono.serializers import AppointmentSerializer


@login_required()
def doctor_view(request, *args, **kwargs):
    return HttpResponse('Doctor view contents!', status=200)


class PatientCheckin(generic.FormView):
    form_class = PatientWhoamiForm
    template_name = 'form_patient_identify.html'

    def form_valid(self, form):
        try:
            patient = form.get_patient()
            return redirect('confirm_appointment', patient=patient.id)
        except Patient.DoesNotExist:
            return redirect('checkin_receptionist')


class PatientConfirmAppointment(generic.FormView):
    form_class = AppointmentChoiceForm
    template_name = 'form_appointment_select.html'

    def get_form_kwargs(self):
        # Note: this is currently a security hole: by tampering with the GET parameter, a bad actor can retrieve a list
        # of all appointments for any patient. Should fix this by implementing a login flow for the user with at LEAST
        # first/last/DOB as authentication credentials; that would prevent at least bored programmers from messing with
        # it, even if that wouldn't secure it against the russians.
        old_kwargs = super(PatientConfirmAppointment, self).get_form_kwargs()
        patient_id = self.kwargs['patient']
        old_kwargs.update({
            'queryset': Appointment.objects.today().filter(patient=patient_id),
            'patient': patient_id,
        })
        return old_kwargs

    def form_valid(self, form):
        # Hit the Appointments API and confirm check-in
        appointment = form.cleaned_data['appointment']
        endpoint = AppointmentEndpoint()
        endpoint.update(appointment.id, {'status': 'Arrived'})
        # Re-sync the appointment info to update the status, and pick up any other updates since last time
        api_data = endpoint.fetch(id=appointment.id)
        serializer = AppointmentSerializer(data=api_data)
        if serializer.is_valid():
            serializer.save()
            return redirect('confirm_info', patient=form.patient)
        else:
            # TODO: set up logging framework properly
            # logger.error("Error saving appointment {}".format(appointment.id))
            return redirect('checkin_receptionist')


class PatientConfirmInfo(generic.FormView):
    """
    Use the API to update demographic info about the patient
    """
    form = PatientInfoForm

    def get_form_kwargs(self):
        api_data = PatientEndpoint().fetch(id=self.request.GET['id'])
        return {'initial': api_data}

    def form_valid(self, form):
        pass


class AppointmentConfirmed(generic.TemplateView):
    template_name = 'checkin_success.html'


class DoctorWelcome(ListView):
    template_name = 'doctor_today.html'
    queryset = Appointment.objects.today()



class CheckinFailed(TemplateView):
    template_name = 'checkin_receptionist.html'