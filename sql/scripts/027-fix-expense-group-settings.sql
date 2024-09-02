-- Script to fix expense groups (reimbursable and CCC)
-- by adding expense_number/claim_number to groups having
-- expense_id but no expense_number OR having report_id but no claim_number

rollback;
begin;

-- expense_group_settings.reimbursable_expense_group_fields
update expense_group_settings
set reimbursable_expense_group_fields = array_append(reimbursable_expense_group_fields, 'expense_number')
where reimbursable_expense_group_fields::text ilike '%expense_id%'
and reimbursable_expense_group_fields::text not ilike '%expense_number%';

update expense_group_settings
set reimbursable_expense_group_fields = array_append(reimbursable_expense_group_fields, 'claim_number')
where reimbursable_expense_group_fields::text ilike '%report_id%'
and reimbursable_expense_group_fields::text not ilike '%claim_number%';


-- expense_group_settings.corporate_credit_card_expense_group_fields
update expense_group_settings
set corporate_credit_card_expense_group_fields = array_append(corporate_credit_card_expense_group_fields, 'expense_number')
where corporate_credit_card_expense_group_fields::text ilike '%expense_id%'
and corporate_credit_card_expense_group_fields::text not ilike '%expense_number%';

update expense_group_settings
set corporate_credit_card_expense_group_fields = array_append(corporate_credit_card_expense_group_fields, 'claim_number')
where corporate_credit_card_expense_group_fields::text ilike '%report_id%'
and corporate_credit_card_expense_group_fields::text not ilike '%claim_number%';

-- Check if all groups have been fixed: Should result in 0s
select count(*) from expense_group_settings where reimbursable_expense_group_fields::text ilike '%expense_id%' and reimbursable_expense_group_fields::text not ilike '%expense_number%';

select count(*) from expense_group_settings where reimbursable_expense_group_fields::text ilike '%report_id%' and reimbursable_expense_group_fields::text not ilike '%claim_number%';

select count(*) from expense_group_settings where corporate_credit_card_expense_group_fields::text ilike '%report_id%' and corporate_credit_card_expense_group_fields::text not ilike '%claim_number%';

select count(*) from expense_group_settings where corporate_credit_card_expense_group_fields::text ilike '%expense_id%' and corporate_credit_card_expense_group_fields::text not ilike '%expense_number%';
