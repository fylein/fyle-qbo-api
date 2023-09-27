from apps.fyle.models import ExpenseGroup
from apps.quickbooks_online.actions import generate_export_url_and_update_expense


def test_generate_export_url_and_update_expense(db):
    expense_group = ExpenseGroup.objects.filter(id=15).first()
    generate_export_url_and_update_expense(expense_group)

    expense_group = ExpenseGroup.objects.filter(id=15).first()

    for expense in expense_group.expenses.all():
        assert expense.accounting_export_summary['url'] == 'https://lolo.qbo.com/app/expense?txnId=370'
        assert expense.accounting_export_summary['synced'] == False
        assert expense.accounting_export_summary['error_type'] == None
        assert expense.accounting_export_summary['id'] == expense.expense_id
        assert expense.accounting_export_summary['state'] == 'COMPLETE'
