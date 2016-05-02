from django.conf.urls import patterns, url
from web_apps.chat import views

urlpatterns = patterns(
    '',
    url(r'^node/(?P<action>.+)/$', views.node_api, name='node_api'),
    url(r'^(?P<cluster_name>.+)/$', views.index, name='cluster'),
    url(r'^$', views.index, name='index'),
)
