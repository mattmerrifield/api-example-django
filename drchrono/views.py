from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.views import generic
from django.views.generic import TemplateView

from drchrono.endpoints import PatientEndpoint, AppointmentEndpoint
from drchrono.forms import PatientWhoamiForm, AppointmentChoiceForm
from drchrono.models import Appointment
from drchrono.serializers import AppointmentSerializer


@login_required()
def doctor_view(request, *args, **kwargs):
    return HttpResponse('Doctor view contents!', status=200)


class PatientCheckin(generic.FormView):
    form_class = PatientWhoamiForm
    template_name = 'form_identify_patient.html'

    def form_valid(self, form):
        # 1) Try to retrieve the patient's appointments today from the cache by first/last/DOB/social
        #    Missing fields here (after the form is validated) were optional to begin with
        data = {f: form.cleaned_data[f] for f in form.cleaned_data if form.cleaned_data[f] is not None}
        # All form fields should be patient attributes, so we can construct filters this cheezy way.
        filters = {"patient__{}".format(f): data[f] for f in data}
        matches = Appointment.objects.filter(**filters)
        if matches.count():
            # Redirect to "select appointment to check in for form
            patient = matches.first().patient
            return redirect('confirm_info', patient=patient.id)
        else:
            return redirect('checkin_failed')  # "No appointments found, please see the receptionist


class PatientConfirmInfo(generic.FormView):
    """
    Use the API to update demographic info about the patient
    """
    def get_form_kwargs(self):
        api_data = PatientEndpoint().fetch(id=self.request.GET['id'])
        return {'initial': api_data}

    def form_valid(self, form):
        pass


class PatientConfirmAppointment(generic.FormView):
    form_class = AppointmentChoiceForm

    def get_form_kwargs(self):
        # Note: this is currently a security hole: by tampering with the GET parameter, a bad actor can retrieve a list
        # of all appointments for any patient. Should fix this by implementing a login flow for the user with at LEAST
        # first/last/DOB as authentication credentials; that would prevent at least bored programmers from messing with
        # it, even if that wouldn't secure it against the russians.
        return {'patient': self.request.GET.get('patient'),
                'start': self.request.GET.get('start'),
                'end': self.request.GET.get('end'),
                }

    def form_valid(self, form):
        # Hit the Appointments API and confirm check-in
        appointment = form.cleaned_data['appointment']
        endpoint = AppointmentEndpoint()
        endpoint.update(
            id=appointment.id,
            data={'status': 'Arrived'},
        )
        # Re-sync the appointment info to update the status, and pick up any other updates since last time
        api_data = endpoint.fetch(id=appointment.id)
        serializer = AppointmentSerializer(data=api_data)
        if serializer.is_valid():
            serializer.save()
        else:
            pass
            # TODO: set up logging framework
            # logger.error("Error saving appointment {}".format(appointment.id))



class AppointmentConfirmed(generic.TemplateView):
    template_name = 'checkin_success.html'



class DoctorWelcome(TemplateView):
    template_name = 'doctor_welcome.html'


class CheckinFailed(TemplateView):
    template_name = 'checkin_failure.html'