rollback;
begin;

update mapping_settings
set import_to_fyle = 't'
where source_field = 'PROJECT' and workspace_id in (select workspace_id from workspace_general_settings where import_projects = 't');

-- fix expense custom properties
update expenses set custom_properties = '{}' where custom_properties is null;
