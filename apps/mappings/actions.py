from django_q.tasks import Chain

from ..workspaces.models import WorkspaceGeneralSettings
from .models import GeneralMapping

def trigger_auto_map_employees(workspace_id: int):
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id, auto_map_employees__isnull=False)

    chain = Chain()

    chain.append(
        'apps.mappings.tasks.async_auto_map_employees', workspace_id)

    general_mappings = GeneralMapping.objects.get(workspace_id=workspace_id)

    if general_mappings.default_ccc_account_name:
        chain.append(
            'apps.mappings.tasks.async_auto_map_ccc_account', workspace_id)

    if chain.length():
        chain.run()