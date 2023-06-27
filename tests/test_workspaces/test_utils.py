import json
import logging
from unittest import mock
from apps.workspaces.utils import generate_qbo_refresh_token
from django.conf import settings

logger = logging.getLogger(__name__)


def test_generate_qbo_refresh_token(db, mocker):
    mocker.patch(
        'apps.workspaces.utils.requests.post',
        return_value=mock.MagicMock(status_code=200, text=json.dumps({'refresh_token': 'sdfghjkl'}))
    )
    generate_qbo_refresh_token('asdfghjkl', settings.QBO_REDIRECT_URI)

    mocker.patch(
        'apps.workspaces.utils.requests.post',
        return_value=mock.MagicMock(status_code=401, text='Wrong client secret or/and refresh token')
    )
    try:
        generate_qbo_refresh_token('asdfghjkl', settings.QBO_REDIRECT_URI)
    except BaseException:
        logger.info('Wrong client secret or/and refresh token')

    mocker.patch(
        'apps.workspaces.utils.requests.post',
        return_value=mock.MagicMock(status_code=404, text='Client ID doesn\'t exist')
    )
    try:
        generate_qbo_refresh_token('asdfghjkl', settings.QBO_REDIRECT_URI)
    except BaseException:
        logger.info('Client ID doesn\'t exist')

    mocker.patch(
        'apps.workspaces.utils.requests.post',
        return_value=mock.MagicMock(status_code=400, text='Some of the parameters were wrong')
    )
    try:
        generate_qbo_refresh_token('asdfghjkl', settings.QBO_REDIRECT_URI)
    except BaseException:
        logger.info('Some of the parameters were wrong')

    mocker.patch(
        'apps.workspaces.utils.requests.post',
        return_value=mock.MagicMock(status_code=500, text='Internal server error')
    )
    try:
        generate_qbo_refresh_token('asdfghjkl', settings.QBO_REDIRECT_URI)
    except BaseException:
        logger.info('Internal server error')
