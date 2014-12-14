# coding: utf-8


def base(request):
    namespace = request.resolver_match.namespace
    view_name = request.resolver_match.view_name

    return {
        'namespace': namespace,
        'view_name': view_name,
    }
