rollback;
being;
update 
  expense_attributes 
set 
  active = true 
where 
  attribute_type in ('PROJECT', 'CATEGORY') 
  and updated_at < now();
