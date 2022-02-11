import pytest
from apps.fyle.models import get_default_expense_state, get_default_expense_group_fields, ExpenseGroupSettings
from .fixtures import data

def test_default_fields():
    expense_group_field = get_default_expense_group_fields()
    expense_state = get_default_expense_state()

    assert expense_group_field == ['employee_email', 'report_id', 'claim_number', 'fund_source']
    assert expense_state == 'PAYMENT_PROCESSING'

@pytest.mark.django_db
def test_expense_group_settings(create_temp_workspace):
    payload = data['expense_group_settings_payload']

    ExpenseGroupSettings.update_expense_group_settings(
        payload, 99
    )

    settings = ExpenseGroupSettings.objects.last()

    assert settings.expense_state == 'PAID'
    assert settings.ccc_export_date_type == 'spent_at'
