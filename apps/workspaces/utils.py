import json
import base64
from typing import Dict

import requests

from django.conf import settings

from future.moves.urllib.parse import urlencode

from qbosdk import UnauthorizedClientError, NotFoundClientError, WrongParamsError, InternalServerError

from .models import WorkspaceGeneralSettings
from fyle_qbo_api.utils import assert_valid


def generate_qbo_refresh_token(authorization_code: str) -> str:
    """
    Generate QBO refresh token from authorization code
    """
    api_data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': settings.QBO_REDIRECT_URI
    }

    auth = '{0}:{1}'.format(settings.QBO_CLIENT_ID, settings.QBO_CLIENT_SECRET)
    auth = base64.b64encode(auth.encode('utf-8'))

    request_header = {
        'Accept': 'application/json',
        'Content-type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic {0}'.format(
            str(auth.decode())
        )
    }

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


def create_or_update_general_settings(general_settings_payload: Dict, workspace_id):
    """
    Create or update general settings
    :param workspace_id:
    :param general_settings_payload: general settings payload
    :return:
    """
    assert_valid(
        'reimbursable_expenses' in general_settings_payload and general_settings_payload[
            'reimbursable_expenses'], 'reimbursable_expenses field is blank')

    assert_valid('non_reimbursable_expenses' in general_settings_payload and general_settings_payload[
        'non_reimbursable_expenses'], 'non_reimbursable_expenses field is blank')

    assert_valid('vendor_mapping' in general_settings_payload and general_settings_payload[
            'vendor_mapping'], 'vendor_mapping field is blank')

    assert_valid('employee_account_mapping' in general_settings_payload and general_settings_payload[
            'employee_account_mapping'], 'employee_account_mapping field is blank')

    general_settings, _ = WorkspaceGeneralSettings.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={
            'reimbursable_expenses': general_settings_payload['reimbursable_expenses'],
            'non_reimbursable_expenses': general_settings_payload['non_reimbursable_expenses'],
            'vendor_mapping': general_settings_payload['vendor_mapping'],
            'employee_account_mapping': general_settings_payload['employee_account_mapping']
        }
    )
    return general_settings
