from django.conf.urls import patterns, url
from web_apps.home import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
)
