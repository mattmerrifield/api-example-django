from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

import views


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    url(r'admin', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'today$', views.doctor_view, name='today'),
    url(r'checkin$', views.checkin_view, name='checkin'),
]
