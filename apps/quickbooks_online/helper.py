from apps.workspaces.models import WorkspaceGeneralSettings
from apps.quickbooks_online.tasks import get_or_create_credit_card_or_debit_card_vendor


def create_vendor_destionation_attribute(name: str, workspace_id: int, general_settings: WorkspaceGeneralSettings):

    created_vendor = get_or_create_credit_card_or_debit_card_vendor(workspace_id, name, False, general_settings)

    return created_vendor
