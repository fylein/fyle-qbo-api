
from apps.mappings.models import GeneralMapping
from apps.mappings.tasks import async_auto_map_ccc_account, async_auto_map_employees
from apps.workspaces.models import WorkspaceGeneralSettings


def trigger_auto_map_employees(workspace_id: int):
    WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id, auto_map_employees__isnull=False)

    async_auto_map_employees(workspace_id=workspace_id)

    general_mappings = GeneralMapping.objects.get(workspace_id=workspace_id)

    if general_mappings.default_ccc_account_name:
        async_auto_map_ccc_account(workspace_id=workspace_id)
