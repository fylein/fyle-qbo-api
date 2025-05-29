from unittest import mock

from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, Mapping
from fyle_integrations_platform_connector import PlatformConnector

from apps.quickbooks_online.utils import QBOConnector
from apps.workspaces.models import FyleCredential, QBOCredential, Workspace, WorkspaceGeneralSettings
from fyle_integrations_imports.modules.categories import Category, disable_categories
from tests.helper import dict_compare_keys
from tests.test_fyle_integrations_imports.test_modules.fixtures import categories_data


def test_sync_destination_attributes(mocker, db):
    workspace_id = 2

    # import categories
    mocker.patch('qbosdk.apis.Accounts.count', return_value=10)
    mocker.patch('qbosdk.apis.Accounts.get_all_generator', return_value=[categories_data['create_new_auto_create_categories_destination_attributes_accounts']])
    mocker.patch('qbosdk.apis.Accounts.get_inactive', return_value=[])
    mocker.patch('qbosdk.apis.Items.get_inactive', return_value=[])

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Account').count()
    assert destination_attributes_count == 63

    category = Category(2, 'ACCOUNT', None,  qbo_connection, ['accounts'], True, False, ['Expense', 'Fixed Asset'])
    category.sync_destination_attributes()

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Account').count()
    assert destination_attributes_count == 66

    # import items
    category = Category(2, 'ACCOUNT', None,  qbo_connection, ['items'], True, False, ['Expense', 'Fixed Asset'])
    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(import_categories=True, import_items=True)
    mocker.patch('qbosdk.apis.Items.count', return_value=10)
    mocker.patch('qbosdk.apis.Items.get_all_generator', return_value=[categories_data['create_new_auto_create_categories_destination_attributes_items']])

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Item').count()
    assert destination_attributes_count == 0

    category.sync_destination_attributes()

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Item').count()
    assert destination_attributes_count == 3

    # import items + import categories
    category = Category(2, 'ACCOUNT', None,  qbo_connection, ['items', 'accounts'], True, False, ['Expense', 'Fixed Asset'])
    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(import_categories=True, import_items=True)
    mocker.patch('qbosdk.apis.Accounts.count', return_value=10)
    mocker.patch('qbosdk.apis.Accounts.get_all_generator', return_value=[categories_data['create_new_auto_create_categories_destination_attributes_accounts_sync']])
    mocker.patch('qbosdk.apis.Items.get_all_generator', return_value=[categories_data['create_new_auto_create_categories_destination_attributes_items_sync']])

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Item').count()
    assert destination_attributes_count == 3

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Account').count()
    assert destination_attributes_count == 66

    category.sync_destination_attributes()

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Item').count()
    assert destination_attributes_count == 5

    destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Account').count()
    assert destination_attributes_count == 68


def test_sync_expense_atrributes(mocker, db):
    workspace_id = 2
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.workspace.fyle_org_id = 'or5qYLrvnoF9'
    fyle_credentials.workspace.save()
    platform = PlatformConnector(fyle_credentials=fyle_credentials)

    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    mocker.patch(
        'fyle.platform.apis.v1.admin.Categories.list_all',
        return_value=[]
    )

    categories_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CATEGORY').count()
    assert categories_count == 279

    category = Category(workspace_id, 'ACCOUNT', None,  qbo_connection, ['accounts', 'items'], True, False, ['Expense', 'Fixed Asset'])
    category.sync_expense_attributes(platform)

    categories_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CATEGORY').count()
    assert categories_count == 279

    mocker.patch(
        'fyle.platform.apis.v1.admin.Categories.list_all',
        return_value=categories_data['create_new_auto_create_categories_expense_attributes_1']
    )
    category.sync_expense_attributes(platform)

    categories_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CATEGORY').count()
    assert categories_count == 284


def test_auto_create_destination_attributes(mocker, db):
    workspace_id = 2
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)

    category = Category(2, 'ACCOUNT', None,  qbo_connection, ['accounts'], True, False, ['Expense', 'Fixed Asset'])
    category.sync_after = None

    Workspace.objects.filter(id=workspace_id).update(fyle_org_id='or5qYLrvnoF9')

    # delete all destination attributes, expense attributes and mappings
    Mapping.objects.filter(workspace_id=workspace_id, source_type='CATEGORY').delete()
    DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT').delete()
    ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CATEGORY').delete()

    mocker.patch(
        'qbosdk.apis.Accounts.count',
        return_value=0
    )
    mocker.patch(
        'qbosdk.apis.Items.count',
        return_value=0
    )
    mocker.patch(
        'qbosdk.apis.Accounts.get_inactive',
        return_value=[]
    )
    mocker.patch(
        'qbosdk.apis.Items.get_inactive',
        return_value=[]
    )
    mocker.patch(
        'qbosdk.apis.Accounts.get_all_generator',
        return_value=[]
    )
    mocker.patch(
        'qbosdk.apis.Items.get_all_generator',
        return_value=[]
    )

    # create new case for categories import
    with mock.patch('fyle.platform.apis.v1.admin.Categories.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Categories.post_bulk',
            return_value=[]
        )
        mocker.patch('qbosdk.apis.Items.count',return_value=0)
        mocker.patch('qbosdk.apis.Items.get_all_generator',return_value=[])
        mocker.patch(
            'qbosdk.apis.Accounts.count',
            return_value=10
        )
        mocker.patch(
            'qbosdk.apis.Accounts.get_all_generator',
            return_value=[categories_data['create_new_auto_create_categories_destination_attributes_accounts']]
        )
        mock_call.side_effect = [
            categories_data['create_new_auto_create_categories_expense_attributes_0'],
            categories_data['create_new_auto_create_categories_expense_attributes_1']
        ]

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'CATEGORY').count()

        assert expense_attributes_count == 0

        destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'ACCOUNT').count()

        assert destination_attributes_count == 0

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='CATEGORY', destination_type='ACCOUNT').count()

        assert mappings_count == 0

        category.trigger_import()

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CATEGORY').count()

        # for categories we dont do time based sync
        assert expense_attributes_count == categories_data['create_new_auto_create_categories_expense_attributes_1'][0]['count']

        destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'ACCOUNT').count()

        assert destination_attributes_count == 3

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='CATEGORY', destination_type='ACCOUNT').count()

        assert mappings_count == 3

    # disable case for categories import
    with mock.patch('fyle.platform.apis.v1.admin.Categories.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Categories.post_bulk',
            return_value=[]
        )
        mocker.patch('qbosdk.apis.Items.count',return_value=0)
        mocker.patch('qbosdk.apis.Items.get_all_generator',return_value=[])
        mocker.patch(
            'qbosdk.apis.Accounts.count',
            return_value=10
        )
        mocker.patch(
            'qbosdk.apis.Accounts.get_inactive',
            return_value=[categories_data['create_new_auto_create_categories_destination_attributes_accounts_disable_case']]
        )
        mock_call.side_effect = [
            categories_data['create_new_auto_create_categories_expense_attributes_1'],
            categories_data['create_new_auto_create_categories_expense_attributes_2']
        ]

        destination_attribute = DestinationAttribute.objects.filter(workspace_id=workspace_id, value='Levi', attribute_type='ACCOUNT').first()

        assert destination_attribute.active == True

        expense_attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, value='Levi', attribute_type='CATEGORY').first()

        assert expense_attribute.active == True

        category_mapping = Mapping.objects.filter(destination_id=destination_attribute.id).first()

        pre_run_expense_attribute_disabled_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, active=False, attribute_type='CATEGORY').count()

        assert pre_run_expense_attribute_disabled_count == 0

        # This confirms that mapping is present and both expense_attribute and destination_attribute are active
        assert category_mapping.source_id == expense_attribute.id

        category.trigger_import()

        destination_attribute = DestinationAttribute.objects.filter(workspace_id=workspace_id, value='Levi', attribute_type='ACCOUNT').first()

        assert destination_attribute.active == False

        expense_attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, value='Levi', attribute_type='CATEGORY').first()

        assert expense_attribute.active == False

        post_run_expense_attribute_disabled_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, active=False, attribute_type='CATEGORY').count()

        assert post_run_expense_attribute_disabled_count == pre_run_expense_attribute_disabled_count + 1

    # not re-enable case for categories import
    with mock.patch('fyle.platform.apis.v1.admin.Categories.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Categories.post_bulk',
            return_value=[]
        )
        mocker.patch('qbosdk.apis.Items.count',return_value=0)
        mocker.patch('qbosdk.apis.Items.get_all_generator',return_value=[])
        mocker.patch(
            'qbosdk.apis.Accounts.count',
            return_value=10
        )
        mocker.patch(
            'qbosdk.apis.Accounts.get_inactive',
            return_value=[categories_data['create_new_auto_create_categories_destination_attributes_accounts']]
        )
        mock_call.side_effect = [
            categories_data['create_new_auto_create_categories_expense_attributes_2'],
            categories_data['create_new_auto_create_categories_expense_attributes_2']
        ]

        pre_run_destination_attribute_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'ACCOUNT', active=False).count()

        assert pre_run_destination_attribute_count == 3

        pre_run_expense_attribute_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'CATEGORY', active=False).count()

        assert pre_run_expense_attribute_count == 1

        category.trigger_import()

        post_run_destination_attribute_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'ACCOUNT', active=False).count()

        assert post_run_destination_attribute_count == pre_run_destination_attribute_count

        post_run_expense_attribute_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'CATEGORY', active=False).count()

        assert pre_run_expense_attribute_count == post_run_expense_attribute_count

    category = Category(2, 'ACCOUNT', None,  qbo_connection, ['accounts', 'items'], True, False, ['Expense', 'Fixed Asset'])
    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(import_categories=True, import_items=True)
    # create new case for items import
    with mock.patch('fyle.platform.apis.v1.admin.Categories.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Categories.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Items.get_all_generator',
            return_value=[categories_data['create_new_auto_create_categories_destination_attributes_items']]
        )
        mocker.patch(
            'qbosdk.apis.Accounts.get_all_generator',
            return_value=[]
        )
        mock_call.side_effect = [
            categories_data['create_new_auto_create_categories_expense_attributes_2'],
            categories_data['create_new_auto_create_categories_expense_attributes_3']
        ]

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'CATEGORY').count()

        assert expense_attributes_count == 5

        destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'ACCOUNT', display_name = 'Item', active=True).count()

        assert destination_attributes_count == 0

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='CATEGORY', destination_type='ACCOUNT').count()

        assert mappings_count == 3

        category.trigger_import()

        expense_attributes_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CATEGORY').count()

        # for categories we dont do time based sync
        assert expense_attributes_count == categories_data['create_new_auto_create_categories_expense_attributes_3'][0]['count']

        destination_attributes_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'ACCOUNT', display_name = 'Item', active=True).count()

        assert destination_attributes_count == 3

        mappings_count = Mapping.objects.filter(workspace_id=workspace_id, source_type='CATEGORY', destination_type='ACCOUNT').count()

        assert mappings_count == 6

    # disable case for items import
    with mock.patch('fyle.platform.apis.v1.admin.Categories.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Categories.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Items.count',
            return_value=10
        )
        mocker.patch(
            'qbosdk.apis.Items.get_inactive',
            return_value=[categories_data['create_new_auto_create_categories_destination_attributes_items_disabled_case']]
        )
        mocker.patch(
            'qbosdk.apis.Accounts.count',
            return_value=0
        )
        mocker.patch(
            'qbosdk.apis.Accounts.get_all_generator',
            return_value=[]
        )
        mock_call.side_effect = [
            categories_data['create_new_auto_create_categories_expense_attributes_3'],
            categories_data['create_new_auto_create_categories_expense_attributes_4']
        ]

        destination_attribute = DestinationAttribute.objects.filter(workspace_id=workspace_id, value='Concrete', attribute_type='ACCOUNT', display_name='Item').first()

        assert destination_attribute.active == True

        expense_attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, value='Concrete', attribute_type='CATEGORY').first()

        assert expense_attribute.active == True

        category_mapping = Mapping.objects.filter(destination_id=destination_attribute.id).first()

        pre_run_expense_attribute_disabled_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, active=False, attribute_type='CATEGORY').count()

        assert pre_run_expense_attribute_disabled_count == 1

        # This confirms that mapping is present and both expense_attribute and destination_attribute are active
        assert category_mapping.source_id == expense_attribute.id

        category.trigger_import()

        destination_attribute = DestinationAttribute.objects.filter(workspace_id=workspace_id, value='Concrete', attribute_type='ACCOUNT', display_name='Item').first()

        assert destination_attribute.active == False

        expense_attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, value='Concrete', attribute_type='CATEGORY').first()

        assert expense_attribute.active == False

        post_run_expense_attribute_disabled_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, active=False, attribute_type='CATEGORY').count()

        assert post_run_expense_attribute_disabled_count == pre_run_expense_attribute_disabled_count + 1

    # not re-enable case for items import
    with mock.patch('fyle.platform.apis.v1.admin.Categories.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Categories.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Items.count',
            return_value=10
        )
        mocker.patch(
            'qbosdk.apis.Items.get_inactive',
            return_value=[categories_data['create_new_auto_create_categories_destination_attributes_items']]
        )
        mocker.patch(
            'qbosdk.apis.Accounts.count',
            return_value=0
        )
        mocker.patch(
            'qbosdk.apis.Accounts.get_all_generator',
            return_value=[]
        )
        mock_call.side_effect = [
            categories_data['create_new_auto_create_categories_expense_attributes_4'],
            categories_data['create_new_auto_create_categories_expense_attributes_4']
        ]

        pre_run_destination_attribute_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'ACCOUNT', active=False, display_name='Item').count()

        assert pre_run_destination_attribute_count == 3

        pre_run_expense_attribute_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'CATEGORY', active=False).count()

        assert pre_run_expense_attribute_count == 2

        category.trigger_import()

        post_run_destination_attribute_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'ACCOUNT', active=False, display_name='Item').count()

        assert post_run_destination_attribute_count == pre_run_destination_attribute_count

        post_run_expense_attribute_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'CATEGORY', active=False).count()

        assert pre_run_expense_attribute_count == post_run_expense_attribute_count

    # Disbale all items case when import_items is False
    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).update(import_items=False)
    with mock.patch('fyle.platform.apis.v1.admin.Categories.list_all') as mock_call:
        mocker.patch(
            'fyle_integrations_platform_connector.apis.Categories.post_bulk',
            return_value=[]
        )
        mocker.patch(
            'qbosdk.apis.Items.count',
            return_value=10
        )
        mocker.patch(
            'qbosdk.apis.Items.get_inactive',
            return_value=[categories_data['create_new_auto_create_categories_destination_attributes_items']]
        )
        mocker.patch(
            'qbosdk.apis.Accounts.count',
            return_value=0
        )
        mocker.patch(
            'qbosdk.apis.Accounts.get_all_generator',
            return_value=[]
        )
        mock_call.side_effect = [
            categories_data['create_new_auto_create_categories_expense_attributes_4'],
            categories_data['create_new_auto_create_categories_expense_attributes_5']
        ]

        pre_run_destination_attribute_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'ACCOUNT', active=False, display_name='Item').count()

        assert pre_run_destination_attribute_count == 3

        pre_run_expense_attribute_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'CATEGORY', active=False).count()

        assert pre_run_expense_attribute_count == 2

        category.trigger_import()

        post_run_destination_attribute_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'ACCOUNT', active=True, display_name='Item').count()

        assert post_run_destination_attribute_count == 0

        item_ids = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'ACCOUNT', display_name='Item').values_list('id', flat=True)
        mapped_source_ids = Mapping.objects.filter(workspace_id=workspace_id, source_type='CATEGORY', destination_type='ACCOUNT', destination_id__in=item_ids).values_list('source_id', flat=True)

        post_run_expense_attribute_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type = 'CATEGORY', active=True, id__in = mapped_source_ids).count()

        assert post_run_expense_attribute_count == 0


def test_construct_fyle_payload(db):
    workspace_id = 3
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    category = Category(workspace_id, 'ACCOUNT', None,  qbo_connection, ['accounts', 'items'], True, False, ['Expense', 'Fixed Asset'])

    # create new case
    paginated_destination_attributes = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Account')
    existing_fyle_attributes_map = {}

    fyle_payload = category.construct_fyle_payload(
        paginated_destination_attributes,
        existing_fyle_attributes_map,
    )

    assert fyle_payload == categories_data['create_fyle_category_payload_create_new_case']

    # disable case
    DestinationAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='ACCOUNT',
        display_name='Account',
        value__in=['Fuel','Advertising']
    ).update(active=False)

    ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        value__in=['Fuel','Advertising']
    ).update(active=True)

    paginated_destination_attributes = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT', display_name='Account')

    paginated_destination_attribute_values = [attribute.value for attribute in paginated_destination_attributes]
    existing_fyle_attributes_map = category.get_existing_fyle_attributes(paginated_destination_attribute_values)

    fyle_payload = category.construct_fyle_payload(
        paginated_destination_attributes,
        existing_fyle_attributes_map
    )

    assert fyle_payload == categories_data['create_fyle_category_payload_create_disable_case']


def test_disable_categories(
    db,
    mocker
):
    workspace_id = 1

    categories_to_disable = {
        'destination_id': {
            'value': 'old_category',
            'updated_value': 'new_category',
            'code': 'old_category_code',
            'updated_code': 'old_category_code'
        }
    }

    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        display_name='Category',
        value='old_category',
        source_id='source_id',
        active=True
    )

    mock_platform = mocker.patch('fyle_integrations_imports.modules.categories.PlatformConnector')
    bulk_post_call = mocker.patch.object(mock_platform.return_value.categories, 'post_bulk')

    disable_categories(workspace_id, categories_to_disable, is_import_to_fyle_enabled=True)

    assert bulk_post_call.call_count == 1

    categories_to_disable = {
        'destination_id': {
            'value': 'old_category_2',
            'updated_value': 'new_category',
            'code': 'old_category_code',
            'updated_code': 'new_category_code'
        }
    }

    disable_categories(workspace_id, categories_to_disable, is_import_to_fyle_enabled=True)
    assert bulk_post_call.call_count == 1

    # Test disable category with code in naming
    general_setting = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    general_setting.import_code_fields = ['ACCOUNT']
    general_setting.save()

    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        display_name='Category',
        value='old_category_code: old_category',
        source_id='source_id_123',
        active=True
    )

    categories_to_disable = {
        'destination_id': {
            'value': 'old_category',
            'updated_value': 'new_category',
            'code': 'old_category_code',
            'updated_code': 'old_category_code'
        }
    }

    payload = [{
        'name': 'old_category_code: old_category',
        'code': 'destination_id',
        'is_enabled': False,
        'id': 'source_id_123'
    }]

    bulk_payload = disable_categories(workspace_id, categories_to_disable, is_import_to_fyle_enabled=True)
    assert bulk_payload == payload


def test_get_existing_fyle_attributes(
    db,
    add_expense_destination_attributes_1,
    add_expense_destination_attributes_3
):
    workspace_id = 1
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    category = Category(1, 'ACCOUNT', None,  qbo_connection, ['items'], True, False, ['Expense', 'Fixed Asset'])

    paginated_destination_attributes = DestinationAttribute.objects.filter(workspace_id=1, attribute_type='ACCOUNT')
    paginated_destination_attributes_without_duplicates = category.remove_duplicate_attributes(paginated_destination_attributes)
    paginated_destination_attribute_values = [attribute.value for attribute in paginated_destination_attributes_without_duplicates]
    existing_fyle_attributes_map = category.get_existing_fyle_attributes(paginated_destination_attribute_values)

    assert existing_fyle_attributes_map == {'internet': '10091', 'meals': '10092'}

    # with code prepending
    category.prepend_code_to_name = True
    paginated_destination_attributes = DestinationAttribute.objects.filter(workspace_id=1, attribute_type='ACCOUNT', code__isnull=False)
    paginated_destination_attributes_without_duplicates = category.remove_duplicate_attributes(paginated_destination_attributes)
    paginated_destination_attribute_values = [attribute.value for attribute in paginated_destination_attributes_without_duplicates]
    existing_fyle_attributes_map = category.get_existing_fyle_attributes(paginated_destination_attribute_values)

    assert existing_fyle_attributes_map == {'123: qbo': '10095'}


def test_construct_fyle_payload_with_code(
    db,
    add_expense_destination_attributes_1,
    add_expense_destination_attributes_3
):
    workspace_id = 1
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    category = Category(1, 'ACCOUNT', None,  qbo_connection, ['items'], True, False, ['Expense', 'Fixed Asset'])
    category.prepend_code_to_name = True

    destination_ids = ['10085', 'Internet', 'Meals']
    paginated_destination_attributes = DestinationAttribute.objects.filter(workspace_id=1, attribute_type='ACCOUNT', destination_id__in=destination_ids)
    paginated_destination_attributes_without_duplicates = category.remove_duplicate_attributes(paginated_destination_attributes)
    paginated_destination_attribute_values = [attribute.value for attribute in paginated_destination_attributes_without_duplicates]
    existing_fyle_attributes_map = category.get_existing_fyle_attributes(paginated_destination_attribute_values)

    # already exists
    fyle_payload = category.construct_fyle_payload(
        paginated_destination_attributes,
        existing_fyle_attributes_map
    )

    assert fyle_payload == []

    # create new case
    existing_fyle_attributes_map = {}
    fyle_payload = category.construct_fyle_payload(
        paginated_destination_attributes,
        existing_fyle_attributes_map
    )

    data = [
        {
            'name': 'Internet',
            'code': 'Internet',
            'is_enabled': True
        },
        {
            'name': 'Meals',
            'code': 'Meals',
            'is_enabled': True
        },
        {
            'name': '123: QBO',
            'code': '10085',
            'is_enabled': True
        }
    ]

    assert dict_compare_keys(fyle_payload, data) == [], 'Keys mismatch'


def test_get_mapped_attributes_ids(db, mocker):
    # Setup: create a Category instance
    workspace_id = 1
    destination_field = 'EXPENSE_CATEGORY'
    qbo_credentials = QBOCredential.get_active_qbo_credentials(workspace_id)
    qbo_connection = QBOConnector(credentials_object=qbo_credentials, workspace_id=workspace_id)
    category = Category(
        workspace_id=workspace_id,
        destination_field=destination_field,
        sync_after=None,
        sdk_connection=qbo_connection,
        destination_sync_methods=['accounts'],
        is_auto_sync_enabled=True,
        is_3d_mapping=False,
        charts_of_accounts=['Expense', 'Fixed Asset']
    )

    # Mock CategoryMapping.objects.filter().values_list()
    errored_attribute_ids = [101, 102, 103]
    expected_mapped_ids = [101, 103]
    mock_qs = mocker.MagicMock()
    mock_qs.values_list.return_value = expected_mapped_ids
    mock_filter = mocker.patch('fyle_accounting_mappings.models.CategoryMapping.objects.filter', return_value=mock_qs)

    # Test for destination_field = 'EXPENSE_CATEGORY'
    result = category.get_mapped_attributes_ids(errored_attribute_ids)
    assert result == expected_mapped_ids
    mock_filter.assert_called_once_with(
        source_category_id__in=errored_attribute_ids,
        destination_expense_head_id__isnull=False
    )

    # Test for destination_field = 'ACCOUNT'
    category.destination_field = 'ACCOUNT'
    mock_filter.reset_mock()
    result = category.get_mapped_attributes_ids(errored_attribute_ids)
    assert result == expected_mapped_ids
    mock_filter.assert_called_once_with(
        source_category_id__in=errored_attribute_ids,
        destination_account_id__isnull=False
    )

    # Test for non-CATEGORY source_field
    category.source_field = 'SOMETHING_ELSE'
    result = category.get_mapped_attributes_ids(errored_attribute_ids)
    assert result == []
