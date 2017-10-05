from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.WebhookResponse.as_view()),
]

