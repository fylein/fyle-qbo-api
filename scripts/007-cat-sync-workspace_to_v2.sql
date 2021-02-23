--- Update existing Workspace General Settings to 'v2' where 'import categories' is not done ---
rollback;
begin;

update
    workspace_general_settings
set
    category_sync_version = 'v2'
where
    workspace_id in
    (
        select
            w.id
        from
            workspaces w
            left join workspace_general_settings gs on gs.workspace_id = w.id
            left join mappings m on (m.workspace_id = w.id and m.source_type = 'CATEGORY')
        where
            w.id not in
            (
                select
                    t.workspace_id
                from
                    task_logs t
                    left join workspaces w on w.id = t.workspace_id
                where
                    t.status in ('COMPLETE', 'FAILED' )
                    and t.type <> 'FETCHING_EXPENSES'
                    and w.name not ilike '%fyle%'
                    and w.name not ilike '%test%'
                    and w.name not ilike '%demo%'
                group by
                    t.workspace_id,
                    w.name,
                    w.fyle_org_id,
                    w.last_synced_at
                order by
                    w.last_synced_at desc
            )
            and w.name not ilike '%fyle%'
            and w.name not ilike '%test%'
            and w.name not ilike '%demo%'
            and gs.reimbursable_expenses_object is not null
            and gs.import_categories is false
        group by
            w.id,
            gs.import_categories
        having count(m.id) <= 10
        order by count(m.id)
    );