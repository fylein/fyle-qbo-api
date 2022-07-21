
import ast
import os
from apps.quickbooks_online.utils import QBOConnector, QBOCredential

github_env_file = os.getenv('GITHUB_ENV')


counter = 0

refresh_tokens = ast.literal_eval(os.environ.get('QBO_TESTS_REFRESH_TOKENS'))
print(refresh_tokens)

for workspace_id in refresh_tokens.keys():
    try:
        qbo_credentials = QBOCredential.objects.get(workspace_id=workspace_id)
        qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

        print('qbo_connection succeded')

    except Exception as error:
        counter += 1
        print('error for workspace id - ', workspace_id)
        print(error)

with open(github_env_file, "a") as env_file:
    env_file.write("num_token_expired=" + counter)
