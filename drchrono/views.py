from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse

@login_required()
def doctor_view(request, *args, **kwargs):
    return HttpResponse('Doctor view contents!', status=200)


def checkin_view(request, *args, **kwargs):
    return HttpResponse("Patient Check-in")