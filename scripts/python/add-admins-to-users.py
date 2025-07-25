from time import sleep

from django.db.models import Q
from fyle_integrations_platform_connector import PlatformConnector

from apps.users.models import User
from apps.workspaces.models import FyleCredential, Workspace

workspaces = Workspace.objects.filter(
    ~Q(name__icontains='fyle for') & ~Q(name__icontains='test')
)

for workspace in workspaces:
    try:
        sleep(1)
        workspace_id = workspace.id
        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
        platform = PlatformConnector(fyle_credentials)
        users = []
        admins = platform.employees.get_admins()
        existing_user_ids = User.objects.values_list('user_id', flat=True)
        for admin in admins:
            # Skip already existing users
            if admin['user_id'] not in existing_user_ids:
                users.append(User(email=admin['email'], user_id=admin['user_id'], full_name=admin['full_name']))
        if len(users):
            created_users = User.objects.bulk_create(users, batch_size=50)
            workspace = Workspace.objects.get(id=workspace_id)
            for user in created_users:
                workspace.user.add(user)
            print('Updated for workspace - ', workspace.name)
    except Exception as e:
        print(e, e.__dict__, '\n\n', workspace.name, workspace.fyle_org_id)
