import logging
from datetime import datetime, timezone

from apps.workspaces.models import QBOCredential, WorkspaceGeneralSettings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_error_model_path() -> str:
    """
    Get error model path: This is for imports submodule
    :return: str
    """
    return 'apps.tasks.models.Error'


def get_import_configuration_model_path() -> str:
    """
    Get import configuration model path: This is for imports submodule
    :return: str
    """
    return 'apps.workspaces.models.WorkspaceGeneralSettings'


def get_app_name() -> str:
    """
    Get Integration Name. This is for imports submodule
    :return: str
    """
    return 'QUICKBOOKS'


def enable_multi_currency_support(workspace_general_settings: WorkspaceGeneralSettings) -> None:
    """
    Enable multi currency support
    :param workspace_general_settings: WorkspaceGeneralSettings
    :return: None
    """
    workspace_id = workspace_general_settings.workspace.id
    qbo_credential = QBOCredential.objects.filter(workspace_id=workspace_id).first()
    if not qbo_credential:
        return

    if qbo_credential.currency and qbo_credential.currency != workspace_general_settings.workspace.fyle_currency:
        logger.info(f'Enabling multi currency support for workspace {workspace_id}')
        WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(
            is_multi_currency_allowed=True,
            updated_at=datetime.now(timezone.utc)
        )
