import json
import base64
from datetime import datetime

import requests

from django.conf import settings

from django_q.models import Schedule
from future.moves.urllib.parse import urlencode

from qbosdk import UnauthorizedClientError, NotFoundClientError, WrongParamsError, InternalServerError


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


def create_schedule(name, workspace_settings, schedule_enabled, next_run, minutes):
    """Create Schedule"""
    next_run = datetime.strptime(next_run, '%Y-%m-%dT%H:%M:00.000Z')

    if schedule_enabled:
        if not workspace_settings.schedule:
            schedule = Schedule.objects.create(
                name=name, func='apps.workspaces.tasks.run_sync_schedule', schedule_type=Schedule.MINUTES,
                args='{}'.format(workspace_settings.workspace_id), minutes=minutes, next_run=next_run
            )
            workspace_settings.schedule = schedule
            workspace_settings.save()
        else:
            schedule = workspace_settings.schedule
            schedule.minutes = minutes
            schedule.name = name
            schedule.next_run = next_run

            schedule.save()
    else:
        if workspace_settings.schedule:
            schedule = workspace_settings.schedule
            workspace_settings.schedule = None
            workspace_settings.save()
            schedule.delete()
