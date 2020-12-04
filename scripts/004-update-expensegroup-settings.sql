-- change expense_state from PAYMENT_PENDING to PAYMENT_PROCESSING
rollback;
begin;

update fyle_expensegroupsettings
set expense_state = 'PAYMENT_PROCESSING'
where fyle_expensegroupsettings.expense_state = 'PAYMENT_PENDING';
