from unittest import mock

from django.conf import settings
from django.db.models import Q
from fyle.platform.exceptions import InternalServerError, RetryException, WrongParamsError
from fyle_accounting_mappings.models import ExpenseAttribute

from apps.fyle.actions import (
    bulk_post_accounting_export_summary,
    create_generator_and_post_in_batches,
    mark_accounting_export_summary_as_synced,
    mark_expenses_as_skipped,
    refresh_fyle_dimension,
    sync_fyle_dimensions,
    update_complete_expenses,
    update_expenses_in_progress,
    update_failed_expenses,
)
from apps.fyle.helpers import get_updated_accounting_export_summary
from apps.fyle.models import Expense, ExpenseGroup
from apps.workspaces.models import FyleCredential, Workspace, WorkspaceGeneralSettings
from fyle_integrations_platform_connector import PlatformConnector


def test_update_expenses_in_progress(db):
    expenses = Expense.objects.filter(org_id='or79Cob97KSh')
    update_expenses_in_progress(expenses)

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    for expense in expenses:
        assert expense.accounting_export_summary['synced'] == False
        assert expense.accounting_export_summary['state'] == 'IN_PROGRESS'
        assert expense.accounting_export_summary['url'] == '{}/main/dashboard'.format(
            settings.QBO_INTEGRATION_APP_URL
        )
        assert expense.accounting_export_summary['error_type'] == None
        assert expense.accounting_export_summary['id'] == expense.expense_id


def test_mark_expenses_as_skipped(db):
    expense_group = ExpenseGroup.objects.filter(workspace_id=3).first()
    expense_id = expense_group.expenses.first().id
    expense_group.expenses.remove(expense_id)

    workspace = Workspace.objects.get(id=3)
    mark_expenses_as_skipped(Q(), [expense_id], workspace)

    expense = Expense.objects.filter(id=expense_id).first()

    assert expense.is_skipped == True
    assert expense.accounting_export_summary['synced'] == False


def test_mark_accounting_export_summary_as_synced(db):
    expenses = Expense.objects.filter(org_id='or79Cob97KSh')
    for expense in expenses:
        expense.accounting_export_summary = get_updated_accounting_export_summary(
            'tx_123',
            'SKIPPED',
            None,
            '{}/main/export_log'.format(settings.QBO_INTEGRATION_APP_URL),
            True
        )
        expense.save()

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    mark_accounting_export_summary_as_synced(expenses)

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    for expense in expenses:
        assert expense.accounting_export_summary['synced'] == True


def test_update_failed_expenses(db):
    expenses = Expense.objects.filter(org_id='or79Cob97KSh')
    update_failed_expenses(expenses, True)

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    for expense in expenses:
        assert expense.accounting_export_summary['synced'] == False
        assert expense.accounting_export_summary['state'] == 'ERROR'
        assert expense.accounting_export_summary['error_type'] == 'MAPPING'
        assert expense.accounting_export_summary['url'] == '{}/main/dashboard'.format(
            settings.QBO_INTEGRATION_APP_URL
        )
        assert expense.accounting_export_summary['id'] == expense.expense_id


def test_update_complete_expenses(db):
    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    update_complete_expenses(expenses, 'https://qbo.google.com')

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    for expense in expenses:
        assert expense.accounting_export_summary['synced'] == False
        assert expense.accounting_export_summary['state'] == 'COMPLETE'
        assert expense.accounting_export_summary['error_type'] == None
        assert expense.accounting_export_summary['url'] == 'https://qbo.google.com'
        assert expense.accounting_export_summary['id'] == expense.expense_id


def test_bulk_post_accounting_export_summary(db):
    fyle_credentails = FyleCredential.objects.get(workspace_id=3)
    platform = PlatformConnector(fyle_credentails)

    with mock.patch('fyle.platform.apis.v1.admin.Expenses.post_bulk_accounting_export_summary') as mock_call:
        mock_call.side_effect = InternalServerError('Timeout')
        try:
            bulk_post_accounting_export_summary(platform, {})
        except RetryException:
            assert mock_call.call_count == 3


def test_create_generator_and_post_in_batches(db):
    fyle_credentails = FyleCredential.objects.get(workspace_id=3)
    platform = PlatformConnector(fyle_credentails)

    with mock.patch('fyle.platform.apis.v1.admin.Expenses.post_bulk_accounting_export_summary') as mock_call:
        mock_call.side_effect = RetryException('Timeout')
        try:
            create_generator_and_post_in_batches([{
                'id': 'txxTi9ZfdepC'
            }], platform, 3)

            # Exception should be handled
            assert True
        except RetryException:
            # This should not be reached
            assert False


def test_handle_post_accounting_export_summary_exception(db):
    fyle_credentails = FyleCredential.objects.get(workspace_id=3)
    platform = PlatformConnector(fyle_credentails)
    expense = Expense.objects.filter(org_id='or79Cob97KSh').first()
    expense.workspace_id = 3
    expense.save()

    expense_id = expense.expense_id

    with mock.patch('fyle.platform.apis.v1.admin.Expenses.post_bulk_accounting_export_summary') as mock_call:
        with mock.patch('fyle.platform.apis.v1.admin.Expenses.get') as mock_expense_get:
            mock_call.side_effect = WrongParamsError('Some of the parameters are wrong', {
                'data': [
                    {
                        'message': 'Permission denied to perform this action.',
                        'key': expense_id
                    }
                ]
            })
            mock_expense_get.return_value = None

            create_generator_and_post_in_batches([{
                'id': expense_id
            }], platform, 3)

    expense = Expense.objects.get(expense_id=expense_id)

    assert expense.accounting_export_summary['synced'] == True
    assert expense.accounting_export_summary['state'] == 'DELETED'
    assert expense.accounting_export_summary['error_type'] == None
    assert expense.accounting_export_summary['url'] == '{}/main/dashboard'.format(
        settings.QBO_INTEGRATION_APP_URL
    )
    assert expense.accounting_export_summary['id'] == expense_id

    expense.accounting_export_summary = get_updated_accounting_export_summary(
        expense_id,
        'IN_PROGRESS',
        None,
        '{}/main/dashboard'.format(settings.QBO_INTEGRATION_APP_URL),
        False
    )
    expense.save()

    with mock.patch('fyle.platform.apis.v1.admin.Expenses.post_bulk_accounting_export_summary') as mock_call:
        with mock.patch('fyle.platform.apis.v1.admin.Expenses.get') as mock_expense_get:
            mock_call.side_effect = WrongParamsError('Some of the parameters are wrong', {
                'data': [
                    {
                        'message': 'Permission denied to perform this action.',
                        'key': expense_id
                    }
                ]
            })
            mock_expense_get.return_value = [{'id': expense_id, 'state': 'APPROVED'}]

            create_generator_and_post_in_batches([{
                'id': expense_id
            }], platform, 3)

    expense = Expense.objects.get(expense_id=expense_id)
    assert expense.accounting_export_summary['synced'] == False
    assert expense.accounting_export_summary['state'] == 'IN_PROGRESS'
    assert expense.accounting_export_summary['id'] == expense_id


def test_sync_fyle_dimensions(db):
    workspace = Workspace.objects.get(id=3)

    with mock.patch('fyle_integrations_platform_connector.fyle_integrations_platform_connector.PlatformConnector.import_fyle_dimensions') as mock_call:
        mock_call.return_value = None

        sync_fyle_dimensions(3)
        assert workspace.source_synced_at is not None

        # If dimensions were synced ≤ 1 day ago, they shouldn't be synced again
        old_source_synced_at = workspace.source_synced_at
        sync_fyle_dimensions(3)
        assert workspace.source_synced_at == old_source_synced_at


def test_sync_fyle_dimensions_with_corporate_credit_card(db):
    """
    Test sync_fyle_dimensions with corporate credit card expenses object set to 'CREDIT CARD PURCHASE'
    """
    workspace = Workspace.objects.get(id=3)
    workspace.source_synced_at = None
    workspace.save()
    workspace_general_settings, created = WorkspaceGeneralSettings.objects.get_or_create(
        workspace_id=3,
        defaults={
            'corporate_credit_card_expenses_object': 'CREDIT CARD PURCHASE'
        }
    )
    if not created:
        workspace_general_settings.corporate_credit_card_expenses_object = 'CREDIT CARD PURCHASE'
        workspace_general_settings.save()

    ExpenseAttribute.objects.get_or_create(
        attribute_type='CORPORATE_CARD',
        workspace_id=3,
        display_name='Test Card 1',
        value='card1',
        source_id='card1',
        defaults={'active': True}
    )

    ExpenseAttribute.objects.get_or_create(
        attribute_type='CORPORATE_CARD',
        workspace_id=3,
        display_name='Test Card 2',
        value='card2',
        source_id='card2',
        defaults={'active': True}
    )

    with mock.patch('fyle_integrations_platform_connector.fyle_integrations_platform_connector.PlatformConnector.import_fyle_dimensions') as mock_import:
        with mock.patch('fyle_qbo_api.utils.patch_integration_settings_for_unmapped_cards') as mock_patch_function:
            mock_import.return_value = None
            sync_fyle_dimensions(3)
            workspace.refresh_from_db()
            workspace_general_settings.refresh_from_db()
            assert workspace_general_settings.corporate_credit_card_expenses_object == 'CREDIT CARD PURCHASE'
            expected_unmapped_count = ExpenseAttribute.objects.filter(
                attribute_type="CORPORATE_CARD",
                workspace_id=3,
                active=True,
                mapping__isnull=True
            ).count()

            mock_patch_function.assert_called_once_with(workspace_id=3, unmapped_card_count=expected_unmapped_count)
            assert workspace.source_synced_at is not None


def test_sync_fyle_dimensions_without_corporate_credit_card(db):
    """
    Test sync_fyle_dimensions with corporate_credit_card_expenses_object not set to 'CREDIT CARD PURCHASE'
    """
    workspace = Workspace.objects.get(id=3)
    workspace.source_synced_at = None
    workspace.save()

    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=3)
    workspace_general_settings.corporate_credit_card_expenses_object = 'BILL'
    workspace_general_settings.save()

    with mock.patch('fyle_integrations_platform_connector.fyle_integrations_platform_connector.PlatformConnector.import_fyle_dimensions') as mock_import:
        with mock.patch('fyle_qbo_api.utils.patch_integration_settings_for_unmapped_cards') as mock_patch_function:
            mock_import.return_value = None
            sync_fyle_dimensions(3)
            workspace.refresh_from_db()
            workspace_general_settings.refresh_from_db()
            assert workspace_general_settings.corporate_credit_card_expenses_object == 'BILL'
            mock_patch_function.assert_not_called()
            assert workspace.source_synced_at is not None


def test_refresh_fyle_dimension(db):
    workspace = Workspace.objects.get(id=3)

    with mock.patch('fyle_integrations_platform_connector.fyle_integrations_platform_connector.PlatformConnector.import_fyle_dimensions') as mock_call:
        mock_call.return_value = None

        refresh_fyle_dimension(3)
        assert workspace.source_synced_at is not None
