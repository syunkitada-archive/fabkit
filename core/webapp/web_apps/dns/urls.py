from django.conf.urls import patterns, url
from web_apps.dns import views

urlpatterns = patterns(
    '',
    url(r'^(?P<cluster_name>.+)/$', views.index, name='index'),
    url(r'^$', views.index, name='index'),
)
