# coding: utf-8

from oslo_config import cfg

CONF = cfg.CONF


def base(request):
    namespace = request.resolver_match.namespace
    view_name = request.resolver_match.view_name
    livereload_js = 'http://{0}:35729/livereload.js'.format(CONF.web.hostname)
    chat_socketio_js = 'http://{0}:4000/socket.io/socket.io.js'.format(CONF.web.hostname)

    return {
        'debug': CONF.web.debug,
        'namespace': namespace,
        'view_name': view_name,
        'livereload_js': livereload_js,
        'chat_socketio_js': chat_socketio_js,
        'web_hostname': CONF.web.hostname,
        'chat_port': 4000,
    }
