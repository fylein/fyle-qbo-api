import base64
import json
import logging
from typing import List

import requests
from django.conf import settings
from future.moves.urllib.parse import urlencode
from fyle_accounting_mappings.models import MappingSetting
from qbosdk import InternalServerError, NotFoundClientError, UnauthorizedClientError, WrongParamsError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, From
)

from apps.workspaces.models import WorkspaceGeneralSettings

logger = logging.getLogger(__name__)
logger.level = logging.INFO


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


def send_email(recipient_email: List[str], subject: str, message: str, sender_email: str):
    """
    Email to the user using sendgrid-sdk

    :param recipient_email: (List[str])
    :param subject: (str)
    :param message: (str)
    :param sender_email: (str)

    :return: None
    """
    SENDGRID_API_KEY = settings.SENDGRID_API_KEY
    sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = From(email=sender_email)
    mail = Mail(
        from_email=from_email,
        to_emails=recipient_email,
        subject=subject,
        html_content=message
    )
    sg.send(mail)
