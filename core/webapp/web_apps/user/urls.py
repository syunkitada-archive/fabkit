from django.conf.urls import patterns, url
from web_apps.user import views

urlpatterns = patterns(
    '',
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^change_password/$', views.change_password, name='change_password'),
    url(r'^create/$', views.create, name='create'),
    url(r'^remove/$', views.remove, name='remove'),
    url(r'^$', views.index, name='index'),
)
