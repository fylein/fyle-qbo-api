-- Script to delete employee mapping setting data since they're moved to workspace general settings

rollback;
begin;

delete from mapping_settings where source_field = 'EMPLOYEE';
