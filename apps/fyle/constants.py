DEFAULT_FYLE_CONDITIONS = [
    {'field_name': 'employee_email', 'type': 'SELECT', 'is_custom': False},
    {'field_name': 'claim_number', 'type': 'TEXT', 'is_custom': False},
    {'field_name': 'report_title', 'type': 'TEXT', 'is_custom': False},
    {'field_name': 'spent_at', 'type': 'DATE', 'is_custom': False},
    {'field_name': 'category', 'type': 'SELECT', 'is_custom': False},
]


REIMBURSABLE_IMPORT_STATE = {
    'PAYMENT_PROCESSING': ['PAYMENT_PROCESSING', 'PAID'],
    'PAID': ['PAID']
}

CCC_IMPORT_STATE = {
    'APPROVED': ['APPROVED', 'PAYMENT_PROCESSING', 'PAID'],
    'PAID': ['PAID']
}
