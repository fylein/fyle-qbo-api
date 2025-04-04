data = {
    'clone_settings_response': {
        "workspace_id": 1,
        "export_settings": {
            "workspace_general_settings": {
                "reimbursable_expenses_object": "EXPENSE",
                "corporate_credit_card_expenses_object": None,
                "name_in_journal_entry": "MERCHANT"
            },
            "expense_group_settings": {
                "reimbursable_expense_group_fields": [
                    "fund_source",
                    "claim_number",
                    "employee_email",
                    "report_id",
                    "test_placeholder"
                ],
                "corporate_credit_card_expense_group_fields": [
                    "fund_source",
                    "claim_number",
                    "employee_email",
                    "report_id",
                    "test_placeholder"
                ],
                "expense_state": "PAYMENT_PROCESSING",
                "ccc_expense_state": None,
                "reimbursable_export_date_type": "current_date",
                "ccc_export_date_type": "current_date",
                "split_expense_grouping": "SINGLE_LINE_ITEM"
            },
            "general_mappings": {
                "accounts_payable": {
                    "name": None,
                    "id": None
                },
                "qbo_expense_account": {
                    "name": "Checking",
                    "id": "35"
                },
                "bank_account": {
                    "name": None,
                    "id": None
                },
                "default_ccc_account": {
                    "name": None,
                    "id": None
                },
                "default_debit_card_account": {
                    "name": None,
                    "id": None
                },
                "default_ccc_vendor": {
                    "name": None,
                    "id": None
                }
            },
            "workspace_id": 1
        },
        "import_settings": {
            "workspace_general_settings": {
                "import_categories": False,
                "import_items": False,
                "charts_of_accounts": [
                    "Expense"
                ],
                "import_tax_codes": False,
                "import_vendors_as_merchants": False,
                "import_code_fields": []
            },
            "general_mappings": {
                "default_tax_code": {
                    "name": None,
                    "id": None
                }
            },
            "mapping_settings": [
                {
                    "source_field": "TEST_PLACEHOLDER",
                    "destination_field": "DEPARTMENT",
                    "import_to_fyle": True,
                    "is_custom": True,
                    "source_placeholder": None
                },
                {
                    "source_field": "COST_CENTER",
                    "destination_field": "CUSTOMER",
                    "import_to_fyle": True,
                    "is_custom": False,
                    "source_placeholder": None
                }
            ],
            "workspace_id": 1
        },
        "advanced_configurations": {
            "workspace_general_settings": {
                "sync_fyle_to_qbo_payments": False,
                "sync_qbo_to_fyle_payments": False,
                "auto_create_destination_entity": False,
                "auto_create_merchants_as_vendors": False,
                "je_single_credit_line": False,
                "change_accounting_period": True,
                "memo_structure": [
                    "employee_email",
                    "category",
                    "spent_on",
                    "report_number",
                    "purpose",
                    "expense_link"
                ]
            },
            "general_mappings": {
                "bill_payment_account": {
                    "id": None,
                    "name": None
                }
            },
            "workspace_schedules": {
                "enabled": True,
                "interval_hours": 24,
                "additional_email_options": [],
                "emails_selected": []
            },
            "workspace_id": 1
        },
        "employee_mappings": {
            "workspace_general_settings": {
                "employee_field_mapping": "EMPLOYEE",
                "auto_map_employees": "NAME"
            },
            "workspace_id": 1
        }
    },
    'clone_settings_missing_values': {
        'export_settings': {},
        'import_settings': None,
        'advanced_settings': False,
        "workspace_id": 1
    },
    'clone_settings': {
        "workspace_id": 1,
        "export_settings": {
            "workspace_general_settings": {
                "reimbursable_expenses_object": "EXPENSE",
                "corporate_credit_card_expenses_object": None,
                "name_in_journal_entry": "MERCHANT"
            },
            "expense_group_settings": {
                "reimbursable_expense_group_fields": [
                    "fund_source",
                    "claim_number",
                    "employee_email",
                    "report_id",
                    "test_placeholder"
                ],
                "corporate_credit_card_expense_group_fields": [
                    "fund_source",
                    "claim_number",
                    "employee_email",
                    "report_id",
                    "test_placeholder"
                ],
                "expense_state": "PAYMENT_PROCESSING",
                "ccc_expense_state": None,
                "reimbursable_export_date_type": "current_date",
                "ccc_export_date_type": "current_date",
                "split_expense_grouping": "SINGLE_LINE_ITEM"
            },
            "general_mappings": {
                "accounts_payable": {
                    "name": None,
                    "id": None
                },
                "qbo_expense_account": {
                    "name": "Checking",
                    "id": "35"
                },
                "bank_account": {
                    "name": None,
                    "id": None
                },
                "default_ccc_account": {
                    "name": None,
                    "id": None
                },
                "default_debit_card_account": {
                    "name": None,
                    "id": None
                },
                "default_ccc_vendor": {
                    "name": None,
                    "id": None
                }
            },
            "workspace_id": 1
        },
        "import_settings": {
            "workspace_general_settings": {
                "import_categories": False,
                "import_items": False,
                "charts_of_accounts": [
                    "Expense"
                ],
                "import_tax_codes": False,
                "import_vendors_as_merchants": False,
                "import_code_fields": []
            },
            "general_mappings": {
                "default_tax_code": {
                    "name": None,
                    "id": None
                }
            },
            "mapping_settings": [
                {
                    "source_field": "TEST_PLACEHOLDER",
                    "destination_field": "DEPARTMENT",
                    "import_to_fyle": True,
                    "is_custom": True,
                    "source_placeholder": None
                },
                {
                    "source_field": "COST_CENTER",
                    "destination_field": "CUSTOMER",
                    "import_to_fyle": True,
                    "is_custom": False,
                    "source_placeholder": None
                }
            ],
            "workspace_id": 1
        },
        "advanced_configurations": {
            "workspace_general_settings": {
                "sync_fyle_to_qbo_payments": False,
                "sync_qbo_to_fyle_payments": False,
                "auto_create_destination_entity": False,
                "auto_create_merchants_as_vendors": False,
                "je_single_credit_line": False,
                "change_accounting_period": True,
                "memo_structure": [
                    "employee_email",
                    "category",
                    "spent_on",
                    "report_number",
                    "purpose",
                    "expense_link"
                ]
            },
            "general_mappings": {
                "bill_payment_account": {
                    "id": None,
                    "name": None
                }
            },
            "workspace_schedules": {
                "enabled": True,
                "interval_hours": 24,
                "additional_email_options": [],
                "emails_selected": []
            },
            "workspace_id": 1
        },
        "employee_mappings": {
            "workspace_general_settings": {
                "employee_field_mapping": "EMPLOYEE",
                "auto_map_employees": "NAME"
            },
            "workspace_id": 1
        }
    },
    'clone_settings_exists': {
        'is_available': True,
        'workspace_name': 'FAE'
    },
    'clone_settings_not_exists': {
        'is_available': False,
        'workspace_name': None
    }
}
