rollback;
begin;
update 
  expense_attributes 
set 
  active = 't' 
where 
  attribute_type in ('PROJECT', 'CATEGORY');
