import json
import base64
from typing import Dict

import requests

from django.conf import settings

from future.moves.urllib.parse import urlencode

from qbosdk import UnauthorizedClientError, NotFoundClientError, WrongParamsError, InternalServerError

from .models import WorkspaceGeneralSettings


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
    general_settings, _ = WorkspaceGeneralSettings.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={
            'reimbursable_expenses_object': general_settings_payload['reimbursable_expenses_object']
            if general_settings_payload['reimbursable_expenses_object'] else None,
            'corporate_credit_card_expenses_object': general_settings_payload['corporate_credit_card_expenses_object']
            if general_settings_payload['corporate_credit_card_expenses_object'] else None,
            'employee_field_mapping': general_settings_payload['employee_field_mapping']
            if general_settings_payload['employee_field_mapping'] else None
        }
    )
    return general_settings
