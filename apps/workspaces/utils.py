import base64
import json
from typing import Dict

import requests
from django.conf import settings
from future.moves.urllib.parse import urlencode
from fyle_accounting_mappings.models import MappingSetting
from qbosdk import InternalServerError, NotFoundClientError, UnauthorizedClientError, WrongParamsError

from apps.fyle.models import ExpenseGroupSettings
from apps.mappings.queues import (
    schedule_auto_map_ccc_employees,
    schedule_auto_map_employees,
    schedule_bill_payment_creation
)
from apps.quickbooks_online.queue import schedule_qbo_objects_status_sync, schedule_reimbursements_sync
from apps.workspaces.models import WorkspaceGeneralSettings
from fyle_qbo_api.utils import assert_valid


def generate_qbo_refresh_token(authorization_code: str, redirect_uri: str) -> str:
    """
    Generate QBO refresh token from authorization code
    """
    api_data = {'grant_type': 'authorization_code', 'code': authorization_code, 'redirect_uri': redirect_uri}

    auth = '{0}:{1}'.format(settings.QBO_CLIENT_ID, settings.QBO_CLIENT_SECRET)
    auth = base64.b64encode(auth.encode('utf-8'))

    request_header = {'Accept': 'application/json', 'Content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic {0}'.format(str(auth.decode()))}

    token_url = settings.QBO_TOKEN_URI
    response = requests.post(url=token_url, data=urlencode(api_data), headers=request_header)

    if response.status_code == 200:
        return json.loads(response.text)['refresh_token']

    elif response.status_code == 401:
        raise UnauthorizedClientError('Wrong client secret or/and refresh token', response.text)

    elif response.status_code == 404:
        raise NotFoundClientError('Client ID doesn\'t exist', response.text)

    elif response.status_code == 400:
        raise WrongParamsError('Some of the parameters were wrong', response.text)

    elif response.status_code == 500:
        raise InternalServerError('Internal server error', response.text)


def delete_cards_mapping_settings(workspace_general_settings: WorkspaceGeneralSettings):
    if not workspace_general_settings.map_fyle_cards_qbo_account or not workspace_general_settings.corporate_credit_card_expenses_object:
        mapping_setting = MappingSetting.objects.filter(workspace_id=workspace_general_settings.workspace_id, source_field='CORPORATE_CARD', destination_field='CREDIT_CARD_ACCOUNT').first()
        if mapping_setting:
            mapping_setting.delete()
