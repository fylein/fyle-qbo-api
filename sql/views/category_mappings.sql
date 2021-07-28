drop view if exists category_mappings_view;

create or replace view category_mappings_view as
select
    m.source_id as source_category_id,
    m.destination_id as destination_account,
    null as destination_expense_head,
    m.workspace_id as workspace_id,
    m.created_at as created_at,
    m.updated_at as updated_at
from
    mappings m
    where m.source_type = 'CATEGORY';
