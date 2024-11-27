from typing import Dict

from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import Workspace, QBOCredential


def get_qbo_connection(query_params: Dict):
    org_id = query_params.get('org_id')

    workspace = Workspace.objects.get(fyle_org_id=org_id)
    workspace_id = workspace.id
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id=workspace.id)

    return QBOConnector(qbo_credentials, workspace_id=workspace_id)


def get_accounting_fields(query_params: Dict):
    qbo_connection = get_qbo_connection(query_params)
    resource_type = query_params.get('resource_type')

    return qbo_connection.get_accounting_fields(resource_type)


def get_exported_entry(query_params: Dict):
    qbo_connection = get_qbo_connection(query_params)
    resource_type = query_params.get('resource_type')
    internal_id = query_params.get('internal_id')

    return qbo_connection.get_exported_entry(resource_type, internal_id)
