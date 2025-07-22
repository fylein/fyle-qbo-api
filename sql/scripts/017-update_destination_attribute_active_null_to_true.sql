rollback;
begin;
update
    destination_attributes
set
    active='t'
where
    active is null;
