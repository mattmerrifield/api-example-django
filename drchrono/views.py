from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.views.generic import TemplateView




@login_required()
def doctor_view(request, *args, **kwargs):
    response = requests.get('https://drchrono.com/api/users/current', headers={
    })
    response.raise_for_status()
    data = response.json()

    # You can store this in your database along with the tokens
    username = data['username']
    return HttpResponse('Doctor view contents!', status=200)


def checkin_view(request, *args, **kwargs):
    return HttpResponse("Patient Check-in")


class DoctorWelcome(TemplateView):
    template_name = 'doctor_welcome.html'

