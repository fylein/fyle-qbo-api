from enum import Enum


class SystemCommentSourceEnum(str, Enum):
    """
    Source function/method that generated the comment
    """
    # Dimension resolution functions
    GET_CCC_ACCOUNT_ID = 'GET_CCC_ACCOUNT_ID'

    # Export functions
    CREATE_BILL = 'CREATE_BILL'
    CREATE_QBO_EXPENSE = 'CREATE_QBO_EXPENSE'
    CREATE_CREDIT_CARD_PURCHASE = 'CREATE_CREDIT_CARD_PURCHASE'

    # Import/sync functions
    HANDLE_EXPENSE_CATEGORY_CHANGE = 'HANDLE_EXPENSE_CATEGORY_CHANGE'
    HANDLE_FUND_SOURCE_CHANGE = 'HANDLE_FUND_SOURCE_CHANGE'
    HANDLE_REPORT_CHANGE = 'HANDLE_REPORT_CHANGE'
    RECREATE_EXPENSE_GROUPS = 'RECREATE_EXPENSE_GROUPS'
    DELETE_EXPENSE_GROUP_AND_RELATED_DATA = 'DELETE_EXPENSE_GROUP_AND_RELATED_DATA'
    DELETE_EXPENSES = 'DELETE_EXPENSES'

    # Expense filtering functions
    GROUP_EXPENSES_AND_SAVE = 'GROUP_EXPENSES_AND_SAVE'


class SystemCommentIntentEnum(str, Enum):
    """
    Intent describing the action taken
    """
    DEFAULT_VALUE_APPLIED = 'DEFAULT_VALUE_APPLIED'
    EMPLOYEE_DEFAULT_VALUE_APPLIED = 'EMPLOYEE_DEFAULT_VALUE_APPLIED'
    UPDATE_EXPENSE_FUND_SOURCE = 'UPDATE_EXPENSE_FUND_SOURCE'
    UPDATE_EXPENSE_CATEGORY = 'UPDATE_EXPENSE_CATEGORY'
    UPDATE_EXPENSE_REPORT = 'UPDATE_EXPENSE_REPORT'
    RECREATE_EXPENSE_GROUPS = 'RECREATE_EXPENSE_GROUPS'
    DELETE_EXPENSE_GROUP = 'DELETE_EXPENSE_GROUP'
    DELETE_EXPENSES = 'DELETE_EXPENSES'
    VENDOR_NOT_FOUND = 'VENDOR_NOT_FOUND'
    SKIP_EXPENSE = 'SKIP_EXPENSE'


class SystemCommentReasonEnum(str, Enum):
    """
    Human readable reason explaining why a particular action was taken
    """
    # Default values applied
    DEFAULT_CCC_ACCOUNT_APPLIED = 'No corporate card mapping found. Using default CCC account from general mappings.'
    DEFAULT_CCC_VENDOR_APPLIED = 'No corporate card to vendor mapping found. Using default CCC vendor from general mappings for bill creation.'

    # Fallback values applied
    EMPLOYEE_CCC_ACCOUNT_APPLIED = 'No corporate card mapping found. Using employee corporate card account from QBO.'

    # Vendor & merchant handling
    CREDIT_CARD_MISC_VENDOR_APPLIED = 'Merchant not found in QuickBooks Online. Using Credit Card Misc vendor as fallback.'
    DEBIT_CARD_MISC_VENDOR_APPLIED = 'Merchant not found in QuickBooks Online. Using Debit Card Misc vendor as fallback.'

    # Fund source & report changes
    FUND_SOURCE_CHANGED = 'Expense payment source was changed from {old} to {new}.'
    CATEGORY_CHANGED = 'Expense category was updated from {old} to {new}.'
    EXPENSE_ADDED_TO_REPORT = 'Expense was added to a report.'
    EXPENSE_EJECTED_FROM_REPORT = 'Expense was removed from its report. Expense has been removed from its expense group.'
    EXPENSE_GROUPS_RECREATED = 'Expense groups were recreated after fund source change.'
    EXPENSE_GROUP_AND_RELATED_DATA_DELETED = 'Expense group and all related data (task logs, errors) were deleted.'
    EXPENSES_DELETED_NO_EXPORT_SETTING = 'Expenses were deleted because no export setting is configured for their fund source (reimbursable/corporate card).'

    # Expense skipping & filtering
    NEGATIVE_EXPENSE_SKIPPED = 'Expense skipped because it has a negative amount.'
    EXPENSE_SKIPPED_AFTER_IMPORT = 'Expense skipped after import due to expense filter rules configured in workspace settings.'
    REIMBURSABLE_EXPENSE_NOT_CONFIGURED = 'Reimbursable expense skipped because reimbursable expense export is not configured.'
    CCC_EXPENSE_NOT_CONFIGURED = 'Corporate card expense skipped because corporate card expense export is not configured.'


class SystemCommentEntityTypeEnum(str, Enum):
    """
    Type of entity the comment is associated with
    """
    EXPENSE = 'EXPENSE'
    EXPENSE_GROUP = 'EXPENSE_GROUP'


class ExportTypeEnum(str, Enum):
    """
    Export type enum
    """
    BILL = 'BILL'
    CHECK = 'CHECK'
    JOURNAL_ENTRY = 'JOURNAL_ENTRY'
    EXPENSE = 'EXPENSE'
    DEBIT_CARD_EXPENSE = 'DEBIT_CARD_EXPENSE'
    CREDIT_CARD_PURCHASE = 'CREDIT_CARD_PURCHASE'
