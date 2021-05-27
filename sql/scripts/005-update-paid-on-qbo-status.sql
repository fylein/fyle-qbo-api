-- Script to set paid_on_qbo as True for existing bills and expenses
rollback;
begin;

-- bills
update bills
set paid_on_qbo = True
where bills.paid_on_qbo = False;

-- expenses
update expenses
set paid_on_qbo = True
where expenses.paid_on_qbo = False;
