from datetime import (
    datetime,
    timezone,
    timedelta
)
from fyle_accounting_mappings.models import (
    DestinationAttribute,
    ExpenseAttribute,
    Mapping
)
from unittest import mock
from apps.workspaces.models import Workspace
from apps.workspaces.models import QBOCredential
from apps.quickbooks_online.utils import QBOConnector
from fyle_integrations_imports.modules.projects import Project
from fyle_integrations_imports.models import ImportLog
from tests.test_fyle_integrations_imports.helpers import (
    get_base_class_instance,
    get_platform_connection
)
from tests.test_fyle_integrations_imports.test_modules.fixtures import projects_data


def test_remove_duplicates(db):
    attributes = DestinationAttribute.objects.filter(attribute_type='CUSTOMER')

    assert len(attributes) == 152

    for attribute in attributes:
        DestinationAttribute.objects.create(
            attribute_type='CUSTOMER',
            workspace_id=attribute.workspace_id,
            value=attribute.value,
            destination_id='010{0}'.format(attribute.destination_id)
        )

    attributes = DestinationAttribute.objects.filter(attribute_type='CUSTOMER')

    assert len(attributes) == 304

    base = get_base_class_instance()

    attributes = base.remove_duplicate_attributes(attributes)
    assert len(attributes) == 65


def test_get_platform_class(db):
    base = get_base_class_instance()
    platform = get_platform_connection(1)

    assert base.get_platform_class(platform) == platform.projects

    base = get_base_class_instance(workspace_id=1, source_field='CATEGORY', destination_field='ACCOUNT', platform_class_name='categories')
    assert base.get_platform_class(platform) == platform.categories

    base = get_base_class_instance(workspace_id=1, source_field='COST_CENTER', destination_field='DEPARTMENT', platform_class_name='cost_centers')
    assert base.get_platform_class(platform) == platform.cost_centers


def test_construct_attributes_filter(db):
    base = get_base_class_instance()

    assert base.construct_attributes_filter('PROJECT') == {'attribute_type': 'PROJECT', 'workspace_id': 1}

    date_string = '2023-08-06 12:50:05.875029'
    sync_after = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')

    base = get_base_class_instance(workspace_id=1, source_field='CATEGORY', destination_field='ACCOUNT', platform_class_name='categories', sync_after=sync_after)

    assert base.construct_attributes_filter('CATEGORY') == {'attribute_type': 'CATEGORY', 'workspace_id': 1, 'updated_at__gte': sync_after}

    paginated_destination_attribute_values = ['Mobile App Redesign', 'Platform APIs', 'Fyle NetSuite Integration', 'Fyle Sage Intacct Integration', 'Support Taxes', 'T&M Project with Five Tasks', 'Fixed Fee Project with Five Tasks', 'General Overhead', 'General Overhead-Current', 'Youtube proj', 'Integrations', 'Yujiro', 'Pickle']

    assert base.construct_attributes_filter('COST_CENTER', paginated_destination_attribute_values) == {'attribute_type': 'COST_CENTER', 'workspace_id': 1, 'updated_at__gte': sync_after, 'value__in': paginated_destination_attribute_values}


def test_expense_attributes_sync_after(db):
    project = get_base_class_instance()

    current_time = datetime.now() - timedelta(minutes=300)
    sync_after = current_time.replace(tzinfo=timezone.utc)
    project.sync_after = sync_after

    expense_attributes = ExpenseAttribute.objects.filter(workspace_id=1, attribute_type='PROJECT')[0:100]

    assert expense_attributes.count() == 100

    paginated_expense_attribute_values = []

    for expense_attribute in expense_attributes:
        expense_attribute.updated_at = datetime.now().replace(tzinfo=timezone.utc)
        expense_attribute.save()
        paginated_expense_attribute_values.append(expense_attribute.value)

    filters = project.construct_attributes_filter('PROJECT', paginated_expense_attribute_values)

    expense_attributes = ExpenseAttribute.objects.filter(**filters)

    assert expense_attributes.count() == 100


def test_auto_create_destination_attributes(mocker, db):
    workspace_id = 3
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    project = Project(3, 'CUSTOMER', None,  qbo_connection, 'customers', True)
    project.sync_after = None

    Workspace.objects.filter(id=workspace_id).update(fyle_org_id='or5qYLrvnoF9')

    # delete all destination attributes, expense attributes and mappings
    Mapping.objects.filter(workspace_id=workspace_id, source_type='PROJECT').delete()
    Mapping.objects.filter(workspace_id=workspace_id, destination_type='CUSTOMER').delete()
    DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CUSTOMER').delete()
    ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='PROJECT').delete()

    with mock.patch('fyle.platform.apis.v1beta.admin.Projects.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Projects.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Customers.count',
            return_value=41
        )
        mocker.patch(
            'qbosdk.apis.Customers.get',
            return_value=projects_data['create_new_auto_create_projects_destination_attributes']
        )
        mock_call.side_effect = [
            projects_data['create_new_auto_create_projects_expense_attributes_0'],
            projects_data['create_new_auto_create_projects_expense_attributes_1']
        ]
        project.trigger_import()

    # Not creating the schedule part due to time diff
    current_time = datetime.now()
    sync_after = current_time.replace(tzinfo=timezone.utc)
    project.sync_after = sync_after

    import_log = ImportLog.objects.filter(workspace_id=workspace_id).first()
    import_log.status = 'COMPLETE'
    import_log.attribute_type = 'PROJECT'
    import_log.total_batches_count = 10
    import_log.processed_batches_count = 10
    import_log.error_log = []
    import_log.save()

    import_log = ImportLog.objects.filter(workspace_id=workspace_id).first()

    response = project.trigger_import()

    import_log_post_run = ImportLog.objects.filter(workspace_id=workspace_id).first()

    assert response == None
    assert import_log.status == import_log_post_run.status
    assert import_log.total_batches_count == import_log_post_run.total_batches_count

    # not creating the schedule due to a schedule running already
    project.sync_after = None

    import_log = ImportLog.objects.filter(workspace_id=workspace_id).first()
    import_log.status = 'IN_PORGRESS'
    import_log.total_batches_count = 8
    import_log.processed_batches_count = 3
    import_log.save()

    response = project.trigger_import()

    assert response == None
    assert import_log.status == 'IN_PORGRESS'
    assert import_log.total_batches_count != 0
    assert import_log.processed_batches_count != 0