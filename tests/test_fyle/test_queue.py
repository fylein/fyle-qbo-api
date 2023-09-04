from apps.fyle.queue import async_post_accounting_export_summary

# This test is just for cov :D
def test_async_post_accounting_export_summary(db):
    async_post_accounting_export_summary(1, 1)
    assert True
