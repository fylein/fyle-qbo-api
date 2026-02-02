from unittest import mock

import pytest
from django.core.cache import cache
from fyle_accounting_library.fyle_platform.enums import FyleAttributeTypeEnum

from fyle_accounting_mappings.models import ExpenseAttribute
from fyle_integrations_imports.models import ImportLog
from fyle_integrations_imports.modules.webhook_attributes import ATTRIBUTE_FIELD_MAPPING, WebhookAttributeProcessor
from tests.test_fyle_integrations_imports.test_modules.fixtures import test_data, webhook_payloads


@pytest.mark.django_db
def test_process_webhook_category_created(db):
    """Test processing CATEGORY CREATED webhook"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = webhook_payloads['category_created']
    initial_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CATEGORY').count()
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        source_id='cat_123'
    ).first()

    assert expense_attr is not None
    assert expense_attr.value == 'Travel / Flight'
    assert expense_attr.active is True
    final_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CATEGORY').count()
    assert final_count > initial_count


@pytest.mark.django_db
def test_process_webhook_category_updated(db):
    """Test processing CATEGORY UPDATED webhook"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        source_id='cat_456'
    ).delete()
    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        source_id='cat_456',
        value='Old Travel',
        active=True
    )
    webhook_body = webhook_payloads['category_updated']
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        source_id='cat_456'
    ).order_by('-updated_at').first()

    assert expense_attr is not None
    assert expense_attr.value == 'New Travel / Train'
    assert expense_attr.active is True


@pytest.mark.django_db
def test_process_webhook_category_deleted(db):
    """Test processing CATEGORY DELETED webhook"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        source_id='cat_789',
        value='Old Category',
        active=True
    )
    webhook_body = webhook_payloads['category_deleted']
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.get(
        workspace_id=workspace_id,
        source_id='cat_789'
    )

    assert expense_attr.active is False


@pytest.mark.django_db
def test_process_webhook_project(db):
    """Test processing PROJECT webhook"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = webhook_payloads['project_created']
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='PROJECT',
        source_id='proj_123'
    ).first()

    assert expense_attr is not None
    assert expense_attr.value == 'Main Project / Sub Project 1'
    assert expense_attr.active is True


@pytest.mark.django_db
def test_process_webhook_employee(db):
    """Test processing EMPLOYEE webhook"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = webhook_payloads['employee_created']
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='EMPLOYEE',
        source_id='emp_123'
    ).first()

    assert expense_attr is not None
    assert expense_attr.value == 'employee@example.com'
    assert expense_attr.detail['user_id'] == 'user_123'
    assert expense_attr.detail['employee_code'] == 'EMP001'
    assert expense_attr.detail['full_name'] == 'John Doe'
    assert expense_attr.detail['location'] == 'New York'
    assert expense_attr.detail['department'] == 'Engineering'
    assert expense_attr.detail['department_code'] == 'ENG'


@pytest.mark.django_db
def test_process_webhook_corporate_card(db):
    """Test processing CORPORATE_CARD webhook"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = webhook_payloads['corporate_card_created']
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='CORPORATE_CARD',
        source_id='card_123'
    ).first()

    assert expense_attr is not None
    # The code extracts last 6 chars which is '2-3456', then removes '-' to get '23456'
    assert expense_attr.value == 'Chase - 23456'
    assert expense_attr.detail['cardholder_name'] == 'Jane Smith'
    assert expense_attr.active is True


@pytest.mark.django_db
def test_process_webhook_corporate_card_created_triggers_patch(db, mocker):
    """Test CORPORATE_CARD CREATED webhook triggers patch and handles exceptions"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)

    with mock.patch('apps.mappings.helpers.patch_corporate_card_integration_settings') as mock_patch:
        processor.process_webhook(webhook_payloads['corporate_card_created'])
        mock_patch.assert_called_once_with(workspace_id=workspace_id)

    with mock.patch('apps.mappings.helpers.patch_corporate_card_integration_settings') as mock_patch:
        mock_patch.side_effect = Exception("Test error")
        processor.process_webhook(webhook_payloads['corporate_card_created'])
        assert ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CORPORATE_CARD',
                                              source_id='card_123').exists()


@pytest.mark.django_db
def test_process_webhook_tax_group(db):
    """Test processing TAX_GROUP webhook"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = webhook_payloads['tax_group_created']
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='TAX_GROUP',
        source_id='tax_123'
    ).first()

    assert expense_attr is not None
    assert expense_attr.value == 'GST 18%'
    assert expense_attr.detail['tax_rate'] == 18.0
    assert expense_attr.active is True


@pytest.mark.django_db
def test_process_expense_field_select_type(db):
    """Test processing SELECT type EXPENSE_FIELD webhook"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = webhook_payloads['expense_field_select_created']
    initial_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='DEPARTMENT'
    ).count()
    processor.process_webhook(webhook_body)

    final_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='DEPARTMENT'
    ).count()

    assert final_count == initial_count + 3
    sales = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='DEPARTMENT',
        value='Sales'
    ).first()
    assert sales is not None
    assert sales.detail['custom_field_id'] == 'field_123'
    assert sales.detail['is_mandatory'] is True


@pytest.mark.django_db
def test_process_expense_field_disable_options(db):
    """Test disabling removed options in SELECT expense field"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='REGION',
        value='North',
        source_id='field_456',
        active=True
    )
    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='REGION',
        value='South',
        source_id='field_456',
        active=True
    )
    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='REGION',
        value='East',
        source_id='field_456',
        active=True
    )
    webhook_body = webhook_payloads['expense_field_region_updated']
    processor.process_webhook(webhook_body)
    east = ExpenseAttribute.objects.get(
        workspace_id=workspace_id,
        attribute_type='REGION',
        value='East'
    )
    assert east.active is False
    north = ExpenseAttribute.objects.get(
        workspace_id=workspace_id,
        attribute_type='REGION',
        value='North'
    )
    assert north.active is True


@pytest.mark.django_db
def test_process_expense_field_non_select_type(db):
    """Test that non-SELECT expense fields are skipped"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = webhook_payloads['expense_field_text_created']
    initial_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='NOTES'
    ).count()
    processor.process_webhook(webhook_body)
    final_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='NOTES'
    ).count()
    assert final_count == initial_count


@pytest.mark.django_db
def test_is_import_in_progress_with_cache(db):
    """Test _is_import_in_progress with caching"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    cache.clear()
    ImportLog.objects.create(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        status='IN_PROGRESS'
    )
    result1 = processor._is_import_in_progress(FyleAttributeTypeEnum.CATEGORY)
    assert result1 is True
    result2 = processor._is_import_in_progress(FyleAttributeTypeEnum.CATEGORY)
    assert result2 is True
    result3 = processor._is_import_in_progress(FyleAttributeTypeEnum.PROJECT)
    assert result3 is False
    cache.clear()


@pytest.mark.django_db
def test_process_webhook_skip_when_import_in_progress(db):
    """Test that webhook processing is skipped when import is in progress"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    cache.clear()
    ImportLog.objects.create(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        status='IN_PROGRESS'
    )
    webhook_body = webhook_payloads['category_skip']
    initial_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='CATEGORY'
    ).count()
    processor.process_webhook(webhook_body)
    final_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='CATEGORY'
    ).count()
    assert final_count == initial_count
    cache.clear()


@pytest.mark.django_db
def test_process_webhook_deleted_ignores_import_in_progress(db):
    """Test that DELETED action processes even when import is in progress"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    cache.clear()
    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='COST_CENTER',
        source_id='cc_delete',
        value='To Be Deleted',
        active=True
    )
    ImportLog.objects.create(
        workspace_id=workspace_id,
        attribute_type='COST_CENTER',
        status='IN_PROGRESS'
    )
    webhook_body = webhook_payloads['cost_center_deleted']
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.get(
        workspace_id=workspace_id,
        source_id='cc_delete'
    )
    assert expense_attr.active is False
    cache.clear()


@pytest.mark.django_db
def test_get_nested_value(db):
    """Test _get_nested_value helper method"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    data = test_data['nested_value_data']
    assert processor._get_nested_value(data, 'user.email') == 'test@example.com'
    assert processor._get_nested_value(data, 'user.profile.department.name') == 'Engineering'
    assert processor._get_nested_value(data, 'user.profile.department.code') == 'ENG'
    # When path doesn't exist, it returns {} as default
    assert processor._get_nested_value(data, 'user.nonexistent.path') == {}
    assert processor._get_nested_value(data, 'completely.wrong.path') == {}


@pytest.mark.django_db
def test_get_attribute_data_category(db):
    """Test _get_attribute_data for CATEGORY type"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    data = test_data['category_with_subcategory']
    result = processor._get_attribute_data(data, FyleAttributeTypeEnum.CATEGORY)
    assert result['value'] == 'Travel / Flight'
    assert result['source_id'] == 'cat_123'
    assert result['active'] is True
    assert result['display_name'] == 'Category'
    assert result['attribute_type'] == 'CATEGORY'


@pytest.mark.django_db
def test_get_attribute_data_category_no_subcategory(db):
    """Test _get_attribute_data for CATEGORY without sub_category"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    data = test_data['category_without_subcategory']
    result = processor._get_attribute_data(data, FyleAttributeTypeEnum.CATEGORY)
    assert result['value'] == 'Travel'
    assert result['source_id'] == 'cat_456'


@pytest.mark.django_db
def test_process_webhook_unsupported_resource_type(db):
    """Test that unsupported resource types are handled gracefully"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = webhook_payloads['unsupported_resource']
    initial_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id).count()
    processor.process_webhook(webhook_body)
    final_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id).count()
    assert final_count == initial_count


@pytest.mark.django_db
def test_attribute_field_mapping_exists():
    """Test that ATTRIBUTE_FIELD_MAPPING contains all expected attribute types"""
    assert FyleAttributeTypeEnum.CATEGORY in ATTRIBUTE_FIELD_MAPPING
    assert FyleAttributeTypeEnum.PROJECT in ATTRIBUTE_FIELD_MAPPING
    assert FyleAttributeTypeEnum.COST_CENTER in ATTRIBUTE_FIELD_MAPPING
    assert FyleAttributeTypeEnum.EMPLOYEE in ATTRIBUTE_FIELD_MAPPING
    assert FyleAttributeTypeEnum.CORPORATE_CARD in ATTRIBUTE_FIELD_MAPPING
    assert FyleAttributeTypeEnum.TAX_GROUP in ATTRIBUTE_FIELD_MAPPING
    assert FyleAttributeTypeEnum.EXPENSE_FIELD in ATTRIBUTE_FIELD_MAPPING
    assert FyleAttributeTypeEnum.DEPENDENT_FIELD in ATTRIBUTE_FIELD_MAPPING
