from django.conf.urls import patterns, url
from apps.result import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
)