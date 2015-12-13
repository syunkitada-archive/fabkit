# coding: utf-8

from oslo_config import cfg

CONF = cfg.CONF


def base(request):
    namespace = request.resolver_match.namespace
    view_name = request.resolver_match.view_name
    livereload_js = 'http://{0}:35729/livereload.js'.format(CONF.web.my_host)

    return {
        'livereload_js': livereload_js,
        'namespace': namespace,
        'view_name': view_name,
    }
