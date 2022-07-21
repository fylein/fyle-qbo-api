
import ast
import os
import pytest
from apps.quickbooks_online.utils import QBOConnector, QBOCredential

@pytest.mark.django_db
def test_token_health():
    refresh_tokens = ast.literal_eval(os.environ.get('QBO_TESTS_REFRESH_TOKENS'))
    counter = 0

    for workspace_id in refresh_tokens.keys():
        try:
            qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)
            qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

            print('qbo_connection succeded', qbo_connection)

        except Exception as error:
            counter += 1
            print('error for workspace id - ', workspace_id)
            print(error)

    with open('test_refresh_token_health.txt', 'w') as file:
        file.write(str(counter))
