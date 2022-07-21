
import ast
import os
import pytest
from apps.quickbooks_online.utils import QBOConnector, QBOCredential

@pytest.mark.django_db
def test_token_health():
    refresh_tokens = ast.literal_eval(os.environ.get('QBO_TESTS_REFRESH_TOKENS'))
    print(refresh_tokens)
    print(os.environ)

    counter = int(os.environ.get('NUM_TOKEN_EXPIRED'))
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
    with open('test_refresh_token_health.txt', 'w') as file:
        file.write(str(counter))


@pytest.mark.django_db
def test_token_health_again():
    refresh_tokens = ast.literal_eval(os.environ.get('QBO_TESTS_REFRESH_TOKENS'))
    print(refresh_tokens)
    print(os.environ)

    counter = int(os.environ.get('NUM_TOKEN_EXPIRED'))
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

    with open('test_refresh_token_health.txt', 'w') as file:
        file.write(str(counter))

    assert 1 == 2
