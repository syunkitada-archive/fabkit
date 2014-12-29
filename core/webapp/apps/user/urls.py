from django.conf.urls import patterns, url
from apps.user import views

urlpatterns = patterns(
    '',
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^change_password/$', views.change_password, name='change_password'),
    url(r'^create_user/$', views.create_user, name='create_user'),
    url(r'^$', views.index, name='index'),
)
