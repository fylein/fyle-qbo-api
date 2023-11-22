from fyle_integrations_imports.modules.base import Base
from fyle_integrations_platform_connector import PlatformConnector
from apps.workspaces.models import FyleCredential, QBOCredential
from apps.quickbooks_online.utils import QBOConnector


def get_base_class_instance(
        workspace_id: int = 1,
        source_field: str='PROJECT',
        destination_field: str = 'PROJECT',
        platform_class_name: str='projects',
        sync_after: str = None,
        destination_sync_method: str = 'customers'
    ):

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    base = Base(
        workspace_id = workspace_id,
        source_field = source_field,
        destination_field = destination_field,
        platform_class_name = platform_class_name,
        sync_after = sync_after,
        sdk_connection = qbo_connection,
        destination_sync_method = destination_sync_method
    )

    return base

def get_platform_connection(workspace_id):
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials=fyle_credentials)

    return platform
