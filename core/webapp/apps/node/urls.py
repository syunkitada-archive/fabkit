from django.conf.urls import patterns, url
from apps.node import views

urlpatterns = patterns(
    '',
    url(r'^(?P<cluster>.+)/$', views.index, name='index'),
    url(r'^$', views.index, name='index'),
)
