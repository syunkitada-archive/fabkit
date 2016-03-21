# coding: utf-8

from oslo_context import context
from oslo_db.sqlalchemy import enginefacade


@enginefacade.transaction_context_provider
class RequestContext(context.RequestContext):
    """Security context and request information.
    Represents the user taking a given action within the system.
    """

    def __init__(self, user_id=None, project_id=None,
                 is_admin=None, read_deleted="no",
                 roles=None, remote_address=None, timestamp=None,
                 request_id=None, auth_token=None, overwrite=True,
                 quota_class=None, user_name=None, project_name=None,
                 service_catalog=None, instance_lock_checked=False,
                 user_auth_plugin=None, **kwargs):

        user = kwargs.pop('user', None)
        tenant = kwargs.pop('tenant', None)
        super(RequestContext, self).__init__(
            auth_token=auth_token,
            user=user_id or user,
            tenant=project_id or tenant,
            domain=kwargs.pop('domain', None),
            user_domain=kwargs.pop('user_domain', None),
            project_domain=kwargs.pop('project_domain', None),
            is_admin=is_admin,
            read_only=kwargs.pop('read_only', False),
            show_deleted=kwargs.pop('show_deleted', False),
            request_id=request_id,
            resource_uuid=kwargs.pop('resource_uuid', None),
            overwrite=overwrite)
