from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

import views


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    url(r'admin', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^today$', views.doctor_view, name='today'),
    url(r'^checkin$', views.PatientCheckin.as_view(), name='checkin'),
    url(r'^update_info$', views.PatientConfirmInfo.as_view(), name='confirm_info'),
    url(r'^confirm_appointment$', views.PatientConfirmAppointment.as_view(), name='confirm_appointment'),
    url(r'^confirmed$', views.AppointmentConfirmed.as_view(), name='confirmed')
    url(r'^welcome$', login_required(views.DoctorWelcome.as_view()), name='welcome'),
]
