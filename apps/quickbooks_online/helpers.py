from apps.fyle.models import ExpenseGroup


def generate_export_type_and_id(expense_group: ExpenseGroup) -> tuple:
    export_type = None
    export_id = None

    if 'Bill' in expense_group.response_logs and expense_group.response_logs['Bill']:
        export_type = 'bill'
        export_id = expense_group.response_logs['Bill']['Id']
    elif 'JournalEntry' in expense_group.response_logs and expense_group.response_logs['JournalEntry']:
        export_type = 'journal'
        export_id = expense_group.response_logs['JournalEntry']['Id']
    elif 'Purchase' in expense_group.response_logs and expense_group.response_logs['Purchase']:
        export_id = expense_group.response_logs['Purchase']['Id']
        if expense_group.response_logs['Purchase']['PaymentType'] == 'Check':
            export_type = 'check'
        else:
            export_type = 'expense'
            if expense_group.fund_source == 'CCC' and \
                expense_group.response_logs['Purchase']['PaymentType'] == 'CreditCard' and \
                    expense_group.response_logs['Purchase'].get('Credit'):
                export_type = 'creditcardcredit'
            elif expense_group.fund_source == 'CCC' \
                and expense_group.response_logs['Purchase']['PaymentType'] == 'Cash':
                export_type = 'expense'

    return export_type, export_id
