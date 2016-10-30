"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'webapp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include('web_apps.api.urls', namespace='api')),
    url(r'^agent/', include('web_apps.agent.urls', namespace='agent')),
    url(r'^task/', include('web_apps.task.urls', namespace='task')),
    url(r'^event/', include('web_apps.event.urls', namespace='event')),
    url(r'^node/', include('web_apps.node.urls', namespace='node')),
    url(r'^user/', include('web_apps.user.urls', namespace='user')),
    url(r'^chat/', include('web_apps.chat.urls', namespace='chat')),
    url(r'^', include('web_apps.home.urls', namespace='home')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
