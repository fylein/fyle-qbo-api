from apps.fyle.models import ExpenseGroup
from apps.quickbooks_online.helpers import generate_export_type_and_id


def test_generate_export_type_and_id(db):
    expense_group = ExpenseGroup.objects.filter(id=15).first()
    print(expense_group.__dict__)
    export_type, export_id = generate_export_type_and_id(expense_group)

    assert export_type == 'expense'
    assert export_id == '370'
