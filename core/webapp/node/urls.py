from django.conf.urls import patterns, url
from node import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
)
