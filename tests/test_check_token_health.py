
import ast
import os
import logging
import pytest
from apps.quickbooks_online.utils import QBOConnector, QBOCredential

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_token_health():
    refresh_tokens = ast.literal_eval(os.environ.get('QBO_TESTS_REFRESH_TOKENS'))
    num_token_expired = 0

    for workspace_id in refresh_tokens.keys():
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)
            qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

            logger.info('qbo_connection succeded - %s', qbo_connection)

        except Exception as error:
            num_token_expired += 1
            logger.info('error for workspace id - %s', workspace_id)
            logger.info('Error message - %s', error)

    logger.info('refresh tokens - %s', ast.literal_eval(os.environ.get('QBO_TESTS_REFRESH_TOKENS')))

    if num_token_expired != 0:
        pytest.exit("Refresh token expired")
