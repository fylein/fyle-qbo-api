-- Script to remove all rows from workspace_schedules
rollback;
begin;

delete from workspace_settings;
delete from workspace_schedules;
