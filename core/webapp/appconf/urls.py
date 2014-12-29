from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'webapp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^fabscript/', include('apps.fabscript.urls', namespace='fabscript')),
    url(r'^node/', include('apps.node.urls', namespace='node')),
    url(r'^result/', include('apps.result.urls', namespace='result')),
    url(r'^user/', include('apps.user.urls', namespace='user')),
    url(r'^', include('apps.home.urls', namespace='home')),
)
