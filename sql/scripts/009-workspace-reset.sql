rollback;
begin;

update task_logs 
SET quickbooks_errors = detail -> 'Fault' -> 'Error' 
where status = 'FAILED' and detail -> 'Fault' is not NULL;

update task_logs 
SET detail=NULL 
where status = 'FAILED' and detail -> 'Fault' is not NULL;