-- Script to move employee mappings data from mappings to employee_mappings table. 
rollback;
begin;

insert into employee_mappings
select 
    row_number() over (order by workspace_id, created_at) as id,
    created_at,
    updated_at,
    destination_card_account_id,
    destination_employee_id,
    destination_vendor_id,
    source_employee_id,
    workspace_id
from employee_mappings_view;
