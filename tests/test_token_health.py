
import ast
import os
import pytest
from apps.quickbooks_online.utils import QBOConnector, QBOCredential

@pytest.mark.django_db
def test_token_health():
    refresh_tokens = ast.literal_eval(os.environ.get('QBO_TESTS_REFRESH_TOKENS'))
    print(refresh_tokens)

    print(os.environ.get('GITHUB_ENV'))
    print(os.environ['GITHUB_ENV'])

    github_env_file = os.getenv('GITHUB_ENV')
    if github_env_file:
        print('Looks like GitHub!')
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

    os.environ['num_token_expired'] = str(counter)
    print("os.environ['num_token_expired']", os.environ['num_token_expired'])
    if github_env_file:
        with open(github_env_file, "a") as env_file:
            env_file.write("num_token_expired=" + counter)

    assert 1 == 2
    