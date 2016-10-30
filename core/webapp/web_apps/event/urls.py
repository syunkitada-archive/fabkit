from django.conf.urls import patterns, url
from web_apps.event import views

urlpatterns = patterns(
    '',
    url(r'^(?P<cluster>.+)/$', views.index, name='index'),
    url(r'^$', views.index, name='index'),
)
