import logging
from datetime import datetime, timezone

from django.conf import settings
from django.db.models import Q
from qbosdk.exceptions import WrongParamsError

from apps.fyle.actions import post_accounting_export_summary, update_complete_expenses
from apps.fyle.models import ExpenseGroup
from apps.mappings.queues import construct_tasks_and_chain_import_fields_to_fyle
from apps.quickbooks_online.helpers import generate_export_type_and_id
from apps.quickbooks_online.utils import QBOConnector
from apps.tasks.models import TaskLog
from apps.workspaces.models import LastExportDetail, QBOCredential, Workspace, WorkspaceGeneralSettings
from fyle_qbo_api.utils import patch_integration_settings

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def update_last_export_details(workspace_id):
    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)

    failed_exports = TaskLog.objects.filter(~Q(type='CREATING_BILL_PAYMENT'), workspace_id=workspace_id, status__in=['FAILED', 'FATAL']).count()

    filters = {
        'workspace_id': workspace_id,
        'status': 'COMPLETE'
    }

    if last_export_detail.last_exported_at:
        filters['updated_at__gt'] = last_export_detail.last_exported_at

    successful_exports = TaskLog.objects.filter(~Q(type__in=['CREATING_BILL_PAYMENT', 'FETCHING_EXPENSES']), **filters).count()

    last_export_detail.failed_expense_groups_count = failed_exports
    last_export_detail.successful_expense_groups_count = successful_exports
    last_export_detail.total_expense_groups_count = failed_exports + successful_exports
    last_export_detail.save()

    patch_integration_settings(workspace_id, errors=failed_exports)
    try:
        post_accounting_export_summary(workspace_id=workspace_id)
    except Exception as e:
        logger.error(f"Error posting accounting export summary: {e} for workspace id {workspace_id}")

    return last_export_detail


def refresh_quickbooks_dimensions(workspace_id: int):
    try:
        quickbooks_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
        quickbooks_connector = QBOConnector(quickbooks_credentials, workspace_id=workspace_id)

        workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()

        if workspace_general_settings:
            construct_tasks_and_chain_import_fields_to_fyle(workspace_id)

        quickbooks_connector.sync_dimensions()

        workspace = Workspace.objects.get(id=workspace_id)
        workspace.destination_synced_at = datetime.now()
        workspace.save(update_fields=['destination_synced_at'])
    except Exception as e:
        logger.info("Error refreshing quickbooks dimensions: %s for workspace id %s", e, workspace_id)


def sync_quickbooks_dimensions(workspace_id: int):
    workspace = Workspace.objects.get(id=workspace_id)
    if workspace.destination_synced_at:
        time_interval = datetime.now(timezone.utc) - workspace.destination_synced_at

    if workspace.destination_synced_at is None or time_interval.days > 0:
        try:
            quickbooks_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
            quickbooks_connector = QBOConnector(quickbooks_credentials, workspace_id=workspace_id)
            quickbooks_connector.sync_dimensions()

            workspace.destination_synced_at = datetime.now()
            workspace.save(update_fields=['destination_synced_at'])
        except WrongParamsError as exception:
            logger.info('QBO token expired workspace_id - %s %s',  workspace_id, {'error': exception.response})
        except Exception as exception:
            logger.exception('Error syncing dimensions workspace_id - %s %s',  workspace_id, {'error': exception.response})


def generate_export_url_and_update_expense(expense_group: ExpenseGroup) -> None:
    """
    Generate export url and update expense
    :param expense_group: Expense Group
    :return: None
    """
    try:
        export_type, export_id = generate_export_type_and_id(expense_group)
        url = '{qbo_app_url}/app/{export_type}?txnId={export_id}'.format(
            qbo_app_url=settings.QBO_APP_URL,
            export_type=export_type,
            export_id=export_id
        )

    except Exception as error:
        # Defaulting it to QBO app url, worst case scenario if we're not able to parse it properly
        url = settings.QBO_APP_URL
        logger.error('Error while generating export url %s', error)

    expense_group.export_url = url
    expense_group.save()

    update_complete_expenses(expense_group.expenses.all(), url)
    post_accounting_export_summary(workspace_id=expense_group.workspace.id, expense_ids=[expense.id for expense in expense_group.expenses.all()], fund_source=expense_group.fund_source)
