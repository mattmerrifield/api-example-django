from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

import views


urlpatterns = [
    url(r'^setup/$', TemplateView.as_view(template_name='kiosk_setup.html'), name='home'),
    url(r'^admin', include(admin.site.urls)),
    url(r'^check-in/$', views.PatientCheckin.as_view(), name='checkin'),
    url(r'^check-in/patient-info/$', views.PatientConfirmInfo.as_view(), name='confirm_info'),
    url(r'^check-in/appointments/$', views.PatientConfirmAppointment.as_view(), name='confirm_appointment'),
    url(r'^check-in/confirmed$', views.AppointmentConfirmed.as_view(), name='checkin_success'),
    url(r'^check-in/receptionist', views.CheckinFailed.as_view(), name='checkin_receptionist'),
    url(r'^doctor/welcome/$', login_required(views.DoctorWelcome.as_view()), name='welcome'),
    url(r'^doctor/today/$', views.doctor_view, name='today'),
    url(r'^$', include('social.apps.django_app.urls', namespace='social')),
]
