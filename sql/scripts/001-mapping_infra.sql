-- Script to make generic mapping infra backward compatible with Quickbooks online integration
-- This script adds a bunch of settings to the settings table
-- These settings are required so that the app does not break

rollback;
begin;

insert into fyle_accounting_mappings_mappingsetting(source_field, destination_field, workspace_id,
                                                    created_at, updated_at)
select
    'EMPLOYEE' as source_field,
    gs.employee_field_mapping as destination_field,
    gs.workspace_id as workspace_id,
    gs.created_at as created_at,
    gs.updated_at as updated_at
from workspaces_workspacegeneralsettings gs;

insert into fyle_accounting_mappings_mappingsetting(source_field, destination_field, workspace_id,
                                                    created_at, updated_at)
select
    'CATEGORY' as source_field,
    'ACCOUNT' as destination_field,
    gs.workspace_id as workspace_id,
    gs.created_at as created_at,
    gs.updated_at as updated_at
from workspaces_workspacegeneralsettings gs;

insert into fyle_accounting_mappings_mappingsetting(source_field, destination_field, workspace_id,
                                                    created_at, updated_at)
select
    'EMPLOYEE' as source_field,
    'CREDIT_CARD_ACCOUNT' as destination_field,
    gs.workspace_id as workspace_id,
    gs.created_at as created_at,
    gs.updated_at as updated_at
from workspaces_workspacegeneralsettings gs
where gs.corporate_credit_card_expenses_object is not null;


insert into fyle_accounting_mappings_expenseattribute(attribute_type, display_name, value, source_id, workspace_id,
                                                      created_at, updated_at)
select
    'EMPLOYEE' as attribute_type,
    'employee' as display_name,
    em.employee_email as value,
    '' as source_id,
    em.workspace_id as workspace_id,
    em.created_at as created_at,
    em.updated_at as updated_at
from mappings_employeemapping em;

insert into fyle_accounting_mappings_expenseattribute(attribute_type, display_name, value, source_id, workspace_id,
                                                      created_at, updated_at)
select
    'CATEGORY' as attribute_type,
    'category' as display_name,
    case when lower(cm.category) = lower(cm.sub_category) then
        cm.category
    else concat(cm.category, ' / ', cm.sub_category) end as value,
    '' as source_id,
    cm.workspace_id as workspace_id,
    cm.created_at as created_at,
    cm.updated_at as updated_at
from mappings_categorymapping cm;

insert into fyle_accounting_mappings_destinationattribute(attribute_type, display_name, value, destination_id,
                                                          workspace_id, created_at, updated_at)
select
    case when em.vendor_display_name is null then
        'EMPLOYEE'
    else
        'VENDOR' end as attribute_type,
    case when em.vendor_display_name is null then
        'employee'
    else
        'vendor' end as display_name,
    case when em.vendor_display_name is null then
        em.employee_display_name
    else
        em.vendor_display_name end as value,
    case when em.vendor_display_name is null then
        em.employee_id
    else
        em.vendor_id end as source_id,
    em.workspace_id as workspace_id,
    now() as created_at,
    now() as updated_at
from mappings_employeemapping em
group by em.vendor_display_name, em.vendor_id, em.employee_id, em.employee_display_name, em.workspace_id;

insert into fyle_accounting_mappings_destinationattribute(attribute_type, display_name, value, destination_id,
                                                          workspace_id, created_at, updated_at)
select
    'CREDIT_CARD_ACCOUNT' as attribute_type,
    'Credit Card Account' as display_name,
    em.ccc_account_name as value,
    em.ccc_account_id as source_id,
    em.workspace_id as workspace_id,
    now() as created_at,
    now() as updated_at
from mappings_employeemapping em
group by em.ccc_account_name, em.ccc_account_id, em.workspace_id;

insert into fyle_accounting_mappings_destinationattribute(attribute_type, display_name, value, destination_id,
                                                          workspace_id, created_at, updated_at)
select
    'ACCOUNT' as attribute_type,
    'account' as display_name,
    cm.account_name as value,
    cm.account_id as destination_id,
    cm.workspace_id as workspace_id,
    now() as created_at,
    now() as updated_at
from mappings_categorymapping cm
group by cm.account_name, cm.account_id, cm.workspace_id;


insert into fyle_accounting_mappings_mapping(source_type, destination_type, source_id, destination_id, workspace_id,
                                             created_at, updated_at)
select
    'EMPLOYEE' as source_type,
    case when em.vendor_display_name is null then
        'EMPLOYEE'
    else
        'VENDOR' end as attribute_type,
    (select id from fyle_accounting_mappings_expenseattribute ea
        where em.employee_email = ea.value and ea.attribute_type = 'EMPLOYEE'
        and em.workspace_id = ea.workspace_id) as source_id,
    case when em.vendor_display_name is null then
        (select id from fyle_accounting_mappings_destinationattribute da where em.workspace_id = da.workspace_id
            and da.attribute_type = 'EMPLOYEE' and da.value = em.employee_display_name)
    else
        (select id from fyle_accounting_mappings_destinationattribute da where em.workspace_id = da.workspace_id
            and da.attribute_type = 'VENDOR' and da.value = em.vendor_display_name) end as destination_id,
    em.workspace_id as workspace_id,
    em.created_at as created_at,
    em.updated_at as updated_at
from mappings_employeemapping em;


insert into fyle_accounting_mappings_mapping(source_type, destination_type, source_id, destination_id, workspace_id,
                                             created_at, updated_at)
select
    'CATEGORY',
    'ACCOUNT',
    (select id from fyle_accounting_mappings_expenseattribute ea where
        (ea.value = case when lower(cm.category) = lower(cm.sub_category) then
            cm.category else concat(cm.category, ' / ', cm.sub_category) end)
        and ea.workspace_id = cm.workspace_id) as source_id,
    (select id from fyle_accounting_mappings_destinationattribute da where da.value = cm.account_name
        and da.workspace_id = cm.workspace_id) as destination_id,
    cm.workspace_id as workspace_id,
    now() as created_at,
    now() as updated_at
from mappings_categorymapping cm;


insert into fyle_accounting_mappings_mapping(source_type, destination_type, source_id, destination_id, workspace_id,
                                             created_at, updated_at)
select
    'EMPLOYEE' as source_type,
    'CREDIT_CARD_ACCOUNT' as destination_type,
    (select id from fyle_accounting_mappings_expenseattribute ea
        where em.employee_email = ea.value and ea.attribute_type = 'EMPLOYEE'
        and em.workspace_id = ea.workspace_id) as source_id,
    (select id from fyle_accounting_mappings_destinationattribute da where
        da.workspace_id = em.workspace_id and em.ccc_account_name = da.value and em.ccc_account_id = da.destination_id
        and da.attribute_type = 'CREDIT_CARD_ACCOUNT') as destination_id,
    em.workspace_id as workspace_id,
    em.created_at as created_at,
    em.updated_at as updated_at
from mappings_employeemapping em;
