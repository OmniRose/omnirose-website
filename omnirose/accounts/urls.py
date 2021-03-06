from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^enter/$', views.EnterView.as_view(), name='enter'),
    url(r'^register/$', views.RegistrationView.as_view(), name='register'),
    url(r'^', include('django.contrib.auth.urls')),
]

