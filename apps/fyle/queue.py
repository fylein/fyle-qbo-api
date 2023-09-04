from django_q.tasks import async_task


def async_post_accounting_export_summary(org_id: str, workspace_id: int) -> None:
    async_task('apps.fyle.tasks.post_accounting_export_summary', org_id, workspace_id)
