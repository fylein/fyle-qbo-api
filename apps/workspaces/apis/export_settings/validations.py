'''
EXPORT SETTINGS API SCHEMA
{
    "workspace_general_settings": {
        "reimbursable_expenses_object": "BILL",
        "corporate_credit_card_expenses_object": "CREDIT CARD PURCHASE"
    },
    "expense_group_settings": {
        "reimbursable_expense_group_fields": [
            "claim_number",
            "report_id",
            "employee_email",
            "fund_source",
            "report_id"
        ],
        "corporate_credit_card_expense_group_fields": [
            "employee_email",
            "fund_source",
            "expense_id",
            "spent_at"
        ],
        "expense_state": "PAYMENT_PROCESSING",
        "reimbursable_export_date_type": "current_date",
        "ccc_export_date_type": "spent_at"
    },
    "general_mappings": {
        "accounts_payable": {
            "name": "Accounts Payable (A/P)",
            "id": "33"
        },
        "qbo_expense_account": {
            "name": null,
            "id": null
        },
        "bank_account": {
            "name": null,
            "id": null
        },
        "default_ccc_account": {
            "name": "Visa",
            "id": "42"
        },
        "default_debit_card_account": {
            "name": null,
            "id": null
        },
        "default_ccc_vendor": {
            "name": "Amazon",
            "id": "10"
        }
    },
    "workspace_id": 1
}
'''
EXPORT_SETTINGS_VALIDATION_TREE = {
    'VENDOR': {
        'reimbursable_expenses_object': {
            'BILL': 'accounts_payable',
            'JOURNAL_ENTRY': 'account_payable',
            'EXPENSE': 'bank_account',
            'expense_group_settings': ['reimbursable_expense_group_fields', 'reimbursable_export_date_type']
        },
        'corporate_credit_card_expenses_object': {
            'BILL': ['accounts_payable', 'default_ccc_vendor'],
            'JOURNAL_ENTRY': 'default_ccc_account',
            'DEBIT CARD EXPENSE': 'default_debit_card_account',
            'CREDIT CARD PURCHASE': 'default_ccc_account',
            'expense_group_settings': ['corporate_credit_card_expense_group_fields', 'ccc_export_date_type']
        }
    },
    'EMPLOYEE': {
        'reimbursable_expenses_object': {
            'BILL': 'accounts_payable',
            'JOURNAL_ENTRY': 'account_payable',
            'EXPENSE': 'bank_account',
            'expense_group_settings': ['reimbursable_expense_group_fields', 'reimbursable_export_date_type']
        },
        'corporate_credit_card_expenses_object': {
            'BILL': ['accounts_payable', 'default_ccc_vendor'],
            'JOURNAL_ENTRY': 'default_ccc_account',
            'DEBIT CARD EXPENSE': 'default_debit_card_account',
            'CREDIT CARD PURCHASE': 'default_ccc_account',
            'expense_group_settings': ['corporate_credit_card_expense_group_fields', 'ccc_export_date_type']
        }
    }
}