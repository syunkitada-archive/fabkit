from django.conf.urls import patterns, url
from web_apps.chat import views

urlpatterns = patterns(
    '',
    url(r'^(?P<cluster>.+)/$', views.index, name='cluster'),
    url(r'^$', views.index, name='index'),
    url(r'^node_api$', views.node_api, name='node_api'),
)
