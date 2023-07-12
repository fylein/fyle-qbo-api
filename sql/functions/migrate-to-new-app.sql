-- Usage: 
-- select migrate_to_new_app(2);
-- 2 is the workspace_id in this case

DROP FUNCTION if exists migrate_to_new_app;

CREATE OR REPLACE FUNCTION migrate_to_new_app(IN _workspace_id integer) RETURNS void AS $$
BEGIN
    RAISE NOTICE 'Migrating workspace % to new QBO App, WOOOHOOOO', _workspace_id;

    UPDATE workspaces set app_version = 'v2' where id = _workspace_id;
    RAISE NOTICE 'Updated workspace % to new QBO App successfully', _workspace_id;

RETURN;
END
$$ LANGUAGE plpgsql;
