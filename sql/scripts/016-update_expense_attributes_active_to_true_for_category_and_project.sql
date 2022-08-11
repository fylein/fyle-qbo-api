rollback;
begin;
update 
  expense_attributes 
set 
  active = true 
where 
  attribute_type in ('PROJECT', 'CATEGORY');
