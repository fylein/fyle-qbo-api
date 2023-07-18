from datetime import datetime, timezone

from django.db.models import Q
from django_q.tasks import Chain
from fyle_accounting_mappings.models import MappingSetting
from qbosdk.exceptions import InvalidTokenError, WrongParamsError
from rest_framework.response import Response
from rest_framework.views import status

from apps.quickbooks_online.utils import QBOConnector
from apps.tasks.models import TaskLog
from apps.workspaces.models import LastExportDetail, QBOCredential, Workspace


def update_last_export_details(workspace_id):
    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)

    failed_exports = TaskLog.objects.filter(~Q(type='CREATING_BILL_PAYMENT'), workspace_id=workspace_id, status__in=['FAILED', 'FATAL']).count()

    successful_exports = TaskLog.objects.filter(~Q(type__in=['CREATING_BILL_PAYMENT', 'FETCHING_EXPENSES']), workspace_id=workspace_id, status='COMPLETE', updated_at__gt=last_export_detail.last_exported_at).count()

    last_export_detail.failed_expense_groups_count = failed_exports
    last_export_detail.successful_expense_groups_count = successful_exports
    last_export_detail.total_expense_groups_count = failed_exports + successful_exports
    last_export_detail.save()

    return last_export_detail


def get_preferences(workspace_id: int):
    try:
        qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)

        qbo_connector = QBOConnector(qbo_credentials, workspace_id=workspace_id)

        preferences = qbo_connector.get_company_preference()

        return Response(data=preferences, status=status.HTTP_200_OK)
    except QBOCredential.DoesNotExist:
        return Response(data={'message': 'QBO credentials not found in workspace'}, status=status.HTTP_400_BAD_REQUEST)
    except (WrongParamsError, InvalidTokenError):
        if qbo_credentials:
            qbo_credentials.refresh_token = None
            qbo_credentials.is_expired = True
            qbo_credentials.save()
        return Response(data={'message': 'Invalid token or Quickbooks Online connection expired'}, status=status.HTTP_400_BAD_REQUEST)


def refresh_quickbooks_dimensions(workspace_id: int):
    quickbooks_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    quickbooks_connector = QBOConnector(quickbooks_credentials, workspace_id=workspace_id)

    mapping_settings = MappingSetting.objects.filter(workspace_id=workspace_id, import_to_fyle=True)
    chain = Chain()

    for mapping_setting in mapping_settings:
        if mapping_setting.source_field == 'PROJECT':
            chain.append('apps.mappings.tasks.auto_import_and_map_fyle_fields', int(workspace_id))
        elif mapping_setting.source_field == 'COST_CENTER':
            chain.append('apps.mappings.tasks.auto_create_cost_center_mappings', int(workspace_id))
        elif mapping_setting.is_custom:
            chain.append('apps.mappings.tasks.async_auto_create_custom_field_mappings', int(workspace_id))

    if chain.length() > 0:
        chain.run()

    quickbooks_connector.sync_dimensions()

    workspace = Workspace.objects.get(id=workspace_id)
    workspace.destination_synced_at = datetime.now()
    workspace.save(update_fields=['destination_synced_at'])


def sync_quickbooks_dimensions(workspace_id: int):
    workspace = Workspace.objects.get(id=workspace_id)
    if workspace.destination_synced_at:
        time_interval = datetime.now(timezone.utc) - workspace.destination_synced_at

    if workspace.destination_synced_at is None or time_interval.days > 0:
        quickbooks_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
        quickbooks_connector = QBOConnector(quickbooks_credentials, workspace_id=workspace_id)
        quickbooks_connector.sync_dimensions()

        workspace.destination_synced_at = datetime.now()
        workspace.save(update_fields=['destination_synced_at'])
