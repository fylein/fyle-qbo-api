-- Script to set exported_at to updated_at of quickbooks_online_bill, quickbooks_online_cheque,
-- quickbooks_online_creditcardpurchase and quickbooks_online_journalentry for existing fyle_expensegroup

rollback;
begin;

-- quickbooks_online_bill
update fyle_expensegroup
set exported_at = quickbooks_online_bill.updated_at
from quickbooks_online_bill
where quickbooks_online_bill.expense_group_id = fyle_expensegroup.id;

-- quickbooks_online_cheque
update fyle_expensegroup
set exported_at = quickbooks_online_cheque.updated_at
from quickbooks_online_cheque
where quickbooks_online_cheque.expense_group_id = fyle_expensegroup.id;

-- quickbooks_online_creditcardpurchase
update fyle_expensegroup
set exported_at = quickbooks_online_creditcardpurchase.updated_at
from quickbooks_online_creditcardpurchase
where quickbooks_online_creditcardpurchase.expense_group_id = fyle_expensegroup.id;

-- quickbooks_online_journalentry
update fyle_expensegroup
set exported_at = quickbooks_online_journalentry.updated_at
from quickbooks_online_journalentry
where quickbooks_online_journalentry.expense_group_id = fyle_expensegroup.id;
