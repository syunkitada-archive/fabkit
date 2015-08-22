# coding: utf-8

from django.conf import settings


def base(request):
    namespace = request.resolver_match.namespace
    view_name = request.resolver_match.view_name
    livereload_js = 'http://{0}:35729/livereload.js'.format(settings.MY_HOST)

    return {
        'livereload_js': livereload_js,
        'namespace': namespace,
        'view_name': view_name,
    }
