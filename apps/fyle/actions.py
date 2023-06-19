from datetime import datetime, timezone
from django.db.models import Q

from fyle_integrations_platform_connector import PlatformConnector

from .constants import DEFAULT_FYLE_CONDITIONS
from apps.workspaces.models import FyleCredential, Workspace
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.fyle.models import ExpenseGroup, ExpenseAttribute

def get_expense_group_ids(workspace_id: int):
    configuration = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    fund_source = []

    if configuration.reimbursable_expenses_object:
        fund_source.append('PERSONAL')
    if configuration.corporate_credit_card_expenses_object:
        fund_source.append('CCC')

    expense_group_ids = ExpenseGroup.objects.filter(
        workspace_id=workspace_id,
        exported_at__isnull=True,
        fund_source__in=fund_source
    ).values_list('id', flat=True)

    return expense_group_ids


def get_expense_fields(workspace_id: int):
    default_attributes = ['EMPLOYEE', 'CATEGORY', 'PROJECT', 'COST_CENTER', 'TAX_GROUP', 'CORPORATE_CARD', 'MERCHANT']

    attributes = ExpenseAttribute.objects.filter(
        ~Q(attribute_type__in=default_attributes),
        workspace_id=workspace_id
    ).values('attribute_type', 'display_name').distinct()

    expense_fields = [
        {'attribute_type': 'COST_CENTER', 'display_name': 'Cost Center'},
        {'attribute_type': 'PROJECT', 'display_name': 'Project'}
    ]

    for attribute in attributes:
        expense_fields.append(attribute)
    
    return expense_fields


def sync_fyle_dimensions(workspace_id: int):
    workspace = Workspace.objects.get(id=workspace_id)
    if workspace.source_synced_at:
        time_interval = datetime.now(timezone.utc) - workspace.source_synced_at

    if workspace.source_synced_at is None or time_interval.days > 0:
        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
        platform = PlatformConnector(fyle_credentials)

        platform.import_fyle_dimensions(import_taxes=True)

        workspace.source_synced_at = datetime.now()
        workspace.save(update_fields=['source_synced_at'])


def refresh_fyle_dimension(workspace_id: int):
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)

    platform.import_fyle_dimensions(import_taxes=True)

    workspace = Workspace.objects.get(id=workspace_id)
    workspace.source_synced_at = datetime.now()
    workspace.save(update_fields=['source_synced_at'])


def get_custom_fields(workspace_id: int):
    fyle_credentails = FyleCredential.objects.get(workspace_id=workspace_id)

    platform = PlatformConnector(fyle_credentails)

    custom_fields = platform.expense_custom_fields.list_all()

    response = []
    response.extend(DEFAULT_FYLE_CONDITIONS)
    for custom_field in custom_fields:
        if custom_field['type'] in ('SELECT', 'NUMBER', 'TEXT'):
            response.append({
                'field_name': custom_field['field_name'],
                'type': custom_field['type'],
                'is_custom': custom_field['is_custom']
            })
    return response
