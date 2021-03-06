from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.utils.timezone import now
from django.views import generic
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.db import models

from drchrono.endpoints import PatientEndpoint, AppointmentEndpoint
from drchrono.forms import PatientWhoamiForm, AppointmentChoiceForm, PatientInfoForm
from drchrono.models import Appointment, Patient
from drchrono.serializers import AppointmentSerializer
from drchrono.sync import sync_all


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
            serializer.save()  # Save updates from API
            serializer.instance.check_in()  # Set checkin time and status
            # Redirect for the next visitor to check in
            return redirect('checkin_success', patient=form.patient)
        else:
            # TODO: set up logging framework properly
            # logger.error("Error saving appointment {}".format(appointment.id))
            return redirect('checkin_receptionist')


class PatientConfirmInfo(generic.FormView):
    """
    Use the API to update demographic info about the patient
    """
    template_name = 'form_patient_info.html'
    form_class = PatientInfoForm

    def get_form_kwargs(self):
        api_data = PatientEndpoint().fetch(id=self.kwargs['patient'])
        return {'initial': api_data}

    def form_valid(self, form):
        pass


class AppointmentConfirmed(generic.TemplateView):
    template_name = 'checkin_success.html'


def sync_info(request):
    "Sync everything, then redirect back to the today screen"
    sync_all()
    return redirect('today')

class DoctorToday(ListView):
    template_name = 'doctor_today.html'
    queryset = Appointment.objects.today()

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorToday, self).get_context_data(**kwargs)
        kwargs['current_time'] = now()
        wait_time = Appointment.objects.filter(
            time_waiting__isnull=False
        ).aggregate(models.Avg('time_waiting'))['time_waiting__avg']
        kwargs['wait_time'] = wait_time
        return kwargs


class CheckinFailed(TemplateView):
    template_name = 'checkin_receptionist.html'


class StartConsult(TemplateView):
    template_name = 'start_consult.html'

    def get(self, request, *args, **kwargs):
        response = super(StartConsult, self).get(request, *args, **kwargs)
        id = self.kwargs['appointment']
        status = 'In Session'

        # Update both API and local cache
        endpoint = AppointmentEndpoint()
        endpoint.update(id, {'status': status})
        Appointment.objects.get(id=id).start_consult()
        return response


class FinishConsult(TemplateView):
    template_name = 'end_consult.html'

    def get(self, request, *args, **kwargs):
        response = super(FinishConsult, self).get(request, *args, **kwargs)
        id = self.kwargs['appointment']
        status = 'Complete'

        # Update both API and local cache
        endpoint = AppointmentEndpoint()
        endpoint.update(id, {'status': status})
        Appointment.objects.get(id=id).finish_consut()
        return response