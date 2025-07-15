from unittest import mock

from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, Mapping
from fyle_integrations_platform_connector import PlatformConnector

from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import FyleCredential, QBOCredential, Workspace, WorkspaceGeneralSettings
from fyle_integrations_imports.modules import Project
from tests.test_fyle_integrations_imports.test_modules.fixtures import projects_data


def test_sync_destination_attributes(mocker, db):
    workspace_id = 3

    mocker.patch('qbosdk.apis.Customers.count', return_value=41)
    mocker.patch('qbosdk.apis.Customers.get_all_generator', return_value=[projects_data['create_new_auto_create_projects_destination_attributes']])
    mocker.patch('qbosdk.apis.Customers.get_inactive', return_value=[])

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=3, attribute_type='CUSTOMER').count()
    assert destination_attributes_count == 29

    project = Project(3, 'CUSTOMER', None,  qbo_connection, ['customers'], True)
    project.sync_destination_attributes()

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=3, attribute_type='CUSTOMER').count()
    assert destination_attributes_count == 43


def test_sync_expense_atrributes(mocker, db):
    workspace_id = 3
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.workspace.fyle_org_id = 'or5qYLrvnoF9'
    fyle_credentials.workspace.save()
    platform = PlatformConnector(fyle_credentials=fyle_credentials)

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    mocker.patch(
        'fyle.platform.apis.v1.admin.Projects.list_all',
        return_value=[]
    )

    projects_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='PROJECT').count()
    assert projects_count == 1222

    project = Project(3, 'CUSTOMER', None,  qbo_connection, 'customers', True)
    project.sync_expense_attributes(platform)

    projects_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='PROJECT').count()
    assert projects_count == 1222

    mocker.patch(
        'fyle.platform.apis.v1.admin.Projects.list_all',
        return_value=projects_data['create_new_auto_create_projects_expense_attributes_0']
    )
    project.sync_expense_attributes(platform)

    projects_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='PROJECT').count()
    assert projects_count == 1223


def test_auto_create_destination_attributes(mocker, db):
    workspace_id = 3
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    project = Project(3, 'CUSTOMER', None,  qbo_connection, ['customers'], True)
    project.sync_after = None

    Workspace.objects.filter(id=workspace_id).update(fyle_org_id='or5qYLrvnoF9')

    # delete all destination attributes, expense attributes and mappings
    Mapping.objects.filter(workspace_id=workspace_id, source_type='PROJECT').delete()
    Mapping.objects.filter(workspace_id=workspace_id, destination_type='CUSTOMER').delete()
    DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CUSTOMER').delete()
    ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='PROJECT').delete()

    mocker.patch('qbosdk.apis.Customers.get_inactive', return_value=[])
    mocker.patch('qbosdk.apis.Customers.get_all_generator', return_value=[])

    # create new case for projects import
    with mock.patch('fyle.platform.apis.v1.admin.Projects.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Projects.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Customers.count',
            return_value=41
        )
        mocker.patch(
            'qbosdk.apis.Customers.get_all_generator',
            return_value=[projects_data['create_new_auto_create_projects_destination_attributes']]
        )
        mock_call.side_effect = [
            projects_data['create_new_auto_create_projects_expense_attributes_0'],
            projects_data['create_new_auto_create_projects_expense_attributes_1']
        ]

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'PROJECT').count()

        assert expense_attributes_count == 0

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='PROJECT', destination_type='CUSTOMER').count()

        assert mappings_count == 0

        project.trigger_import()

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'PROJECT').count()

        assert expense_attributes_count == projects_data['create_new_auto_create_projects_expense_attributes_1'][0]['count']

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='PROJECT', destination_type='CUSTOMER').count()

        assert mappings_count == 3

    # disable case for project import
    with mock.patch('fyle.platform.apis.v1.admin.Projects.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Projects.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Customers.count',
            return_value=39
        )
        mocker.patch(
            'qbosdk.apis.Customers.get_inactive',
            return_value=[projects_data['create_new_auto_create_projects_destination_attributes_disable_case']]
        )
        mock_call.side_effect = [
            projects_data['create_new_auto_create_projects_expense_attributes_3'],
            projects_data['create_new_auto_create_projects_expense_attributes_4']
        ]

        destination_attribute = DestinationAttribute.objects.filter(workspace_id=workspace_id, value='David').first()

        assert destination_attribute.active == True

        expense_attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, value='David').first()

        assert expense_attribute.active == True

        mapping = Mapping.objects.filter(destination_id=destination_attribute.id).first()

        pre_run_expense_attribute_disabled_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, active=False, attribute_type='PROJECT').count()

        assert pre_run_expense_attribute_disabled_count == 0

        # This confirms that mapping is present and both expense_attribute and destination_attribute are active
        assert mapping.source_id == expense_attribute.id

        project.trigger_import()

        destination_attribute = DestinationAttribute.objects.filter(workspace_id=workspace_id, value='David').first()

        assert destination_attribute.active == False

        expense_attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, value='David').first()

        assert expense_attribute.active == False

        post_run_expense_attribute_disabled_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, active=False, attribute_type='PROJECT').count()

        assert post_run_expense_attribute_disabled_count == 2

    # not re-enable case for project import
    with mock.patch('fyle.platform.apis.v1.admin.Projects.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Projects.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Customers.count',
            return_value=41
        )
        # In case of QBO the not re-enable case of destination attribute is same as create new case, the disabled values when re-enabled will only be added
        mocker.patch(
            'qbosdk.apis.Customers.get_inactive',
            return_value=[projects_data['create_new_auto_create_projects_destination_attributes']]
        )
        mock_call.side_effect = [
            projects_data['create_new_auto_create_projects_expense_attributes_3'],
            projects_data['create_new_auto_create_projects_expense_attributes_4']
        ]

        pre_run_destination_attribute_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'CUSTOMER', active=False).count()

        assert pre_run_destination_attribute_count == 40

        pre_run_expense_attribute_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'PROJECT', active=False).count()

        assert pre_run_expense_attribute_count == 2

        project.trigger_import()

        post_run_destination_attribute_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'CUSTOMER', active=False).count()

        assert post_run_destination_attribute_count == pre_run_destination_attribute_count + 1

        post_run_expense_attribute_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'PROJECT', active=False).count()

        assert pre_run_expense_attribute_count == post_run_expense_attribute_count


def test_disable_projects(db, mocker):
    from fyle_integrations_imports.modules.projects import disable_projects
    workspace_id = 1

    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(import_code_fields=[])

    projects_to_disable = {
        'destination_id': {
            'value': 'old_project',
            'updated_value': 'new_project',
            'code': 'old_project_code',
            'updated_code': 'old_project_code'
        }
    }

    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='PROJECT',
        display_name='Project',
        value='old_project',
        source_id='source_id',
        active=True
    )

    mock_platform = mocker.patch('fyle_integrations_imports.modules.projects.PlatformConnector')
    bulk_post_call = mocker.patch.object(mock_platform.return_value.projects, 'post_bulk')

    disable_projects(workspace_id, projects_to_disable, is_import_to_fyle_enabled=True)

    assert bulk_post_call.call_count == 1

    projects_to_disable = {
        'destination_id': {
            'value': 'old_project_2',
            'updated_value': 'new_project',
            'code': 'old_project_code',
            'updated_code': 'new_project_code'
        }
    }

    disable_projects(workspace_id, projects_to_disable, is_import_to_fyle_enabled=True)
    assert bulk_post_call.call_count == 1

    # Test disable project with code in naming
    general_setting = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    general_setting.import_code_fields = ['JOB']
    general_setting.save()

    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='PROJECT',
        display_name='Project',
        value='old_project_code: old_project',
        source_id='source_id_123',
        active=True
    )

    projects_to_disable = {
        'destination_id': {
            'value': 'old_project',
            'updated_value': 'new_project',
            'code': 'old_project_code',
            'updated_code': 'old_project_code'
        }
    }

    payload = [{
        'name': 'old_project_code: old_project',
        'code': 'destination_id',
        'description': mocker.ANY,  # Description is dynamic
        'is_enabled': False,
        'id': 'source_id_123'
    }]

    bulk_payload = disable_projects(workspace_id, projects_to_disable, is_import_to_fyle_enabled=True)
    # Only check keys and values except description
    for actual, expected in zip(bulk_payload, payload):
        for k in expected:
            assert actual[k] == expected[k] or expected[k] == mocker.ANY
