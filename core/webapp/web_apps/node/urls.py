from django.conf.urls import patterns, url
from web_apps.node import views

urlpatterns = patterns(
    '',
    url(r'^(?P<cluster>.+)/get_console/$', views.get_console, name='get_console'),
    url(r'^(?P<cluster>.+)/$', views.index, name='index'),
    url(r'^$', views.index, name='index'),
)
