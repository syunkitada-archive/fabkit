from django.conf.urls import patterns, url
from apps.fabscript import views

urlpatterns = patterns(
    '',
    url(r'^remove/$', views.remove, name='remove'),
    url(r'^$', views.index, name='index'),
)
