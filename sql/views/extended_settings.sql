drop view if exists extended_settings_view;

create or replace view extended_settings_view as
select
    w.id as workspace_id,
    w.name as workspace_name,
    w.fyle_org_id as fyle_org_id,
    w.last_synced_at as last_synced_at,
    w.source_synced_at as source_synced_at,
    w.destination_synced_at as destination_synced_at,
    wgs.employee_field_mapping as employee_field_mapping,
    wgs.reimbursable_expenses_object as reimbursable_expenses_object,
    wgs.corporate_credit_card_expenses_object as corporate_credit_card_expenses_object,
    wgs.import_projects as import_projects,
    wgs.import_categories as import_categories,
    wgs.sync_fyle_to_qbo_payments as sync_fyle_to_qbo_payments,
    wgs.sync_qbo_to_fyle_payments as sync_qbo_to_fyle_payments,
    wgs.auto_map_employees as auto_map_employees,
    wgs.category_sync_version as category_sync_version,
    wgs.auto_create_destination_entity as auto_create_destination_entity,
    wgs.map_merchant_to_vendor as map_merchant_to_vendor,
    wgs.je_single_credit_line as je_single_credit_line,
    gm.bank_account_name as bank_account_name,
    gm.bank_account_id as bank_account_id,
    gm.default_ccc_account_name as default_ccc_account_name,
    gm.default_ccc_account_id as default_ccc_account_id,
    gm.accounts_payable_name as accounts_payable_name,
    gm.accounts_payable_id as accounts_payable_id,
    gm.default_ccc_vendor_name as default_ccc_vendor_name,
    gm.default_ccc_vendor_id as default_ccc_vendor_id,
    gm.bill_payment_account_name as bill_payment_account_name,
    gm.bill_payment_account_id as bill_payment_account_id,
    gm.qbo_expense_account_name as qbo_expense_account_name,
    gm.qbo_expense_account_id as qbo_expense_account_id,
    egs.reimbursable_expense_group_fields as reimbursable_expense_group_fields,
    egs.corporate_credit_card_expense_group_fields as corporate_credit_card_expense_group_fields,
    egs.export_date_type as export_date_type,
    egs.expense_state as expense_state
from
    workspaces w
left join workspace_general_settings wgs on wgs.workspace_id = w.id
left join general_mappings gm on gm.workspace_id = w.id
left join expense_group_settings egs on egs.workspace_id = w.id
;
