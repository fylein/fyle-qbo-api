from datetime import datetime, timezone
from typing import List

from django.conf import settings
from django.db.models import Q

from fyle_integrations_platform_connector import PlatformConnector
from fyle_accounting_mappings.models import ExpenseAttribute

from apps.fyle.constants import DEFAULT_FYLE_CONDITIONS
from apps.fyle.models import ExpenseGroup, Expense
from apps.workspaces.models import FyleCredential, Workspace, WorkspaceGeneralSettings

from .helpers import get_updated_accounting_export_summary


def get_expense_group_ids(workspace_id: int):
    configuration = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    fund_source = []

    if configuration.reimbursable_expenses_object:
        fund_source.append('PERSONAL')
    if configuration.corporate_credit_card_expenses_object:
        fund_source.append('CCC')

    expense_group_ids = ExpenseGroup.objects.filter(workspace_id=workspace_id, exported_at__isnull=True, fund_source__in=fund_source).values_list('id', flat=True)

    return expense_group_ids


def get_expense_fields(workspace_id: int):
    default_attributes = ['EMPLOYEE', 'CATEGORY', 'PROJECT', 'COST_CENTER', 'TAX_GROUP', 'CORPORATE_CARD', 'MERCHANT']

    attributes = ExpenseAttribute.objects.filter(~Q(attribute_type__in=default_attributes), workspace_id=workspace_id).values('attribute_type', 'display_name').distinct()

    expense_fields = [{'attribute_type': 'COST_CENTER', 'display_name': 'Cost Center'}, {'attribute_type': 'PROJECT', 'display_name': 'Project'}]

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
            response.append({'field_name': custom_field['field_name'], 'type': custom_field['type'], 'is_custom': custom_field['is_custom']})
    return response


def __bulk_update_expenses(expense_to_be_updated: List[Expense]) -> None:
    """
    Bulk update expenses
    :param expense_to_be_updated: expenses to be updated
    :return: None
    """
    if expense_to_be_updated:
        Expense.objects.bulk_update(expense_to_be_updated, ['is_skipped', 'accounting_export_summary'], batch_size=50)


def update_expenses_in_progress(in_progress_expenses: List[Expense]) -> None:
    """
    Update expenses in progress in bulk
    :param in_progress_expenses: in progress expenses
    :return: None
    """
    expense_to_be_updated = []
    for expense in in_progress_expenses:
        expense_to_be_updated.append(
            Expense(
                id=expense.id,
                accounting_export_summary=get_updated_accounting_export_summary(
                    expense.expense_id,
                    'IN_PROGRESS',
                    None,
                    '{}/workspaces/main/dashboard'.format(settings.QBO_INTEGRATION_APP_URL),
                    False
                )
            )
        )

    __bulk_update_expenses(expense_to_be_updated)


def mark_expenses_as_skipped(final_query: Q, expenses_object_ids: List, workspace: Workspace) -> None:
    """
    Mark expenses as skipped in bulk
    :param final_query: final query
    :param expenses_object_ids: expenses object ids
    :param workspace: workspace object
    :return: None
    """
    # We'll iterate through the list of expenses to be skipped, construct accounting export summary and update expenses
    expense_to_be_updated = []
    expenses_to_be_skipped = Expense.objects.filter(
        final_query,
        id__in=expenses_object_ids,
        expensegroup__isnull=True,
        org_id=workspace.fyle_org_id
    )

    for expense in expenses_to_be_skipped:
        expense_to_be_updated.append(
            Expense(
                id=expense.id,
                is_skipped=True,
                accounting_export_summary=get_updated_accounting_export_summary(
                    expense.expense_id,
                    'SKIPPED',
                    None,
                    '{}/workspaces/main/export_log'.format(settings.QBO_INTEGRATION_APP_URL),
                    False
                )
            )
        )

    __bulk_update_expenses(expense_to_be_updated)


def mark_accounting_export_summary_as_synced(expenses: List[Expense]) -> None:
    """
    Mark accounting export summary as synced in bulk
    :param expenses: List of expenses
    :return: None
    """
    # Mark all expenses as synced
    expense_to_be_updated = []
    for expense in expenses:
        expense.accounting_export_summary['synced'] = True
        updated_accounting_export_summary = expense.accounting_export_summary
        expense_to_be_updated.append(
            Expense(
                id=expense.id,
                accounting_export_summary=updated_accounting_export_summary
            )
        )

    Expense.objects.bulk_update(expense_to_be_updated, ['accounting_export_summary'], batch_size=50)

def update_failed_expenses(in_progress_expenses: List[Expense], is_mapping_error: bool) -> None:
    """
    Update failed expenses
    :param in_progress_expenses: In progress expenses
    """
    expense_to_be_updated = []
    for expense in in_progress_expenses:
        expense_to_be_updated.append(
            Expense(
                id=expense.id,
                accounting_export_summary=get_updated_accounting_export_summary(
                    expense.expense_id,
                    'ERROR',
                    'MAPPING' if is_mapping_error else 'ACCOUNTING_INTEGRATION_ERROR',
                    '{}/workspaces/main/dashboard'.format(settings.QBO_INTEGRATION_APP_URL),
                    False
                )
            )
        )

    __bulk_update_expenses(expense_to_be_updated)
