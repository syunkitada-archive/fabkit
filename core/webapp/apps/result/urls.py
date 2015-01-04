from django.conf.urls import patterns, url
from apps.result import views

urlpatterns = patterns(
    '',
    url(r'^remove/$', views.remove, name='remove'),
    url(r'^(?P<cluster>\d+)/$', views.index, name='index'),
    url(r'^$', views.index, name='index'),
)
