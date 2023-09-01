import logging
import json
from datetime import datetime

from django.conf import settings

from apps.fyle.helpers import post_request
from apps.mappings.queue import schedule_bill_payment_creation
from apps.quickbooks_online.queue import schedule_qbo_objects_status_sync, schedule_reimbursements_sync
from apps.workspaces.models import WorkspaceGeneralSettings, FyleCredential

logger = logging.getLogger(__name__)
logger.level = logging.INFO


class AdvancedConfigurationsTriggers:
    """
    Class containing all triggers for advanced_configurations
    """

    @staticmethod
    def run_workspace_general_settings_triggers(workspace_general_settings_instance: WorkspaceGeneralSettings):
        """
        Run workspace general settings triggers
        """
        schedule_bill_payment_creation(sync_fyle_to_qbo_payments=workspace_general_settings_instance.sync_fyle_to_qbo_payments, workspace_id=workspace_general_settings_instance.workspace.id)

        schedule_qbo_objects_status_sync(sync_qbo_to_fyle_payments=workspace_general_settings_instance.sync_qbo_to_fyle_payments, workspace_id=workspace_general_settings_instance.workspace.id)

        schedule_reimbursements_sync(sync_qbo_to_fyle_payments=workspace_general_settings_instance.sync_qbo_to_fyle_payments, workspace_id=workspace_general_settings_instance.workspace.id)

    @staticmethod
    def post_to_integration_settings(workspace_id: int):
        """
        Post to integration settings
        """
        refresh_token = FyleCredential.objects.get(workspace_id=workspace_id).refresh_token
        url = '{}/integrations/'.format(settings.INTEGRATIONS_SETTINGS_API)
        payload = {
            'tpa_id': settings.FYLE_CLIENT_ID,
            'tpa_name': 'Fyle Quickbooks Integration',
            'type': 'ACCOUNTING',
            'is_active': True,
            'connected_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        }

        try:
            post_request(url, json.dumps(payload), refresh_token)
        except Exception as error:
            logger.error(error)
