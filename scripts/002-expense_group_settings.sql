-- Script to add expense groups settings to existing workspaces
rollback;
begin;

update workspaces_workspacegeneralsettings
set corporate_credit_card_expenses_object = 'JOURNAL ENTRY'
where corporate_credit_card_expenses_object = 'JOURNAL_ENTRY';


update workspaces_workspacegeneralsettings
set reimbursable_expenses_object = 'JOURNAL ENTRY'
where reimbursable_expenses_object = 'JOURNAL_ENTRY';

insert into fyle_expensegroupsettings(
    reimbursable_expense_group_fields,
    corporate_credit_card_expense_group_fields,
    expense_states,
    export_date,
    created_at,
    updated_at,
    workspace_id
) select
   case when famm.destination_field = 'DEPARTMENT' and gs.reimbursable_expenses_object != 'JOURNAL ENTRY' then
    (
        select'{"employee_email", "report_id", "claim_number", "fund_source", "' || lower(famm.source_field) || '"}'
    )::varchar[]
   else
       '{"employee_email", "report_id", "claim_number", "fund_source"}'
   end as reimbursable_expense_group_fields,
   case when famm.destination_field = 'DEPARTMENT' and gs.corporate_credit_card_expenses_object != 'JOURNAL ENTRY' then
   (
        select'{"employee_email", "report_id", "claim_number", "fund_source", "' || lower(famm.source_field) || '"}'
    )::varchar[]
   else
       '{"employee_email", "report_id", "claim_number", "fund_source"}'
   end as corporate_credit_card_expense_group_fields,
   '{"PAYMENT_PROCESSING"}' as expense_states,
   'CURRENT_DATE' as export_date,
   now() as created_at,
   now() as updated_at,
   w.id as workspace_id
from workspaces_workspace w
left join workspaces_workspacegeneralsettings gs on w.id = gs.workspace_id
left join fyle_accounting_mappings_mappingsetting famm on (
    w.id = famm.workspace_id and famm.destination_field = 'DEPARTMENT')
order by w.id;