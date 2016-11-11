from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.views import generic
from django.views.generic import TemplateView

from drchrono.endpoints import PatientEndpoint


@login_required()
def doctor_view(request, *args, **kwargs):
    return HttpResponse('Doctor view contents!', status=200)


class PatientCheckin(generic.FormView):
    def form_valid(self, form):
        # 1) Try to retrieve the patient id from the cache by first/last/DOB/social
        # 2)

        PatientEndpoint.get()


class DoctorWelcome(TemplateView):
    template_name = 'doctor_welcome.html'

