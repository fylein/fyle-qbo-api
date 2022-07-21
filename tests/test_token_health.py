
import ast
import os
import pytest
from apps.quickbooks_online.utils import QBOConnector, QBOCredential

@pytest.mark.django_db
def test_token_health():
    refresh_tokens = ast.literal_eval(os.environ.get('QBO_TESTS_REFRESH_TOKENS'))
    print(refresh_tokens)
    print(os.environ)

    counter = os.environ.get('NUM_TOKEN_EXPIRED')
    print(counter)
    print(type(counter))

    for workspace_id in refresh_tokens.keys():
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)
            qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

            print('qbo_connection succeded', qbo_connection)

        except Exception as error:
            counter += 1
            print('error for workspace id - ', workspace_id)
            print(error)

    os.environ['TOKEN_HEALTH_COUNT'] = str(counter)
    print("os.environ['TOKEN_HEALTH_COUNT']", os.environ['TOKEN_HEALTH_COUNT'])

    assert 1 == 2
