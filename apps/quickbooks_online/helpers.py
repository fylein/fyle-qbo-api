from apps.fyle.models import ExpenseGroup


def generate_export_type_and_id(expense_group: ExpenseGroup) -> tuple:
    """
    Generate export type and id
    :param expense_group: Expense group object
    """
    export_type = None
    export_id = None

    # If Bill exists, export_type is bill
    if 'Bill' in expense_group.response_logs and expense_group.response_logs['Bill']:
        export_type = 'bill'
        export_id = expense_group.response_logs['Bill']['Id']
    # If JournalEntry exists, export_type is journal
    elif 'JournalEntry' in expense_group.response_logs and expense_group.response_logs['JournalEntry']:
        export_type = 'journal'
        export_id = expense_group.response_logs['JournalEntry']['Id']
    # If Purchase exists, export_type can be check / expense
    elif 'Purchase' in expense_group.response_logs and expense_group.response_logs['Purchase']:
        export_id = expense_group.response_logs['Purchase']['Id']
        # If PaymentType is Check, export_type is check
        if expense_group.response_logs['Purchase']['PaymentType'] == 'Check':
            export_type = 'check'
        else:
            # Defaulting to expense initially
            export_type = 'expense'
            # If PaymentType is CreditCard, export_type is creditcardcredit
            if expense_group.fund_source == 'CCC' and \
                expense_group.response_logs['Purchase']['PaymentType'] == 'CreditCard' and \
                    expense_group.response_logs['Purchase'].get('Credit'):
                export_type = 'creditcardcredit'
            # If PaymentType is Cash, export_type is expense
            elif expense_group.fund_source == 'CCC' \
                and expense_group.response_logs['Purchase']['PaymentType'] == 'Cash':
                export_type = 'expense'

    return export_type, export_id
