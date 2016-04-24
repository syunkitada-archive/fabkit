from django.conf.urls import patterns, url
from web_apps.agent import views

urlpatterns = patterns(
    '',
    url(r'^(?P<cluster>.+)/$', views.index, name='index'),
    url(r'^$', views.index, name='index'),
)
