# coding: utf-8

from oslo_config import cfg

CONF = cfg.CONF


def base(request):
    namespace = request.resolver_match.namespace
    view_name = request.resolver_match.view_name
    livereload_js = 'http://{0}:35729/livereload.js'.format(
        CONF.web.node_public_host)
    chat_socketio_js = 'http://{0}:{1}/socket.io/socket.io.js'.format(
        CONF.web.node_public_host, CONF.web.node_public_port)

    return {
        'debug': CONF.web.debug,
        'namespace': namespace,
        'view_name': view_name,
        'livereload_js': livereload_js,
        'chat_socketio_js': chat_socketio_js,
        'web_hostname': CONF.web.node_public_host,
        'chat_port': CONF.web.node_public_port,
    }
