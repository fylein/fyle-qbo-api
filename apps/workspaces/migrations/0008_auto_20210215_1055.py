# Generated by Django 3.0.3 on 2021-02-15 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [('django_q', '0010_auto_20200610_0856'), ('workspaces', '0007_auto_20210120_1851')]

    operations = [
        migrations.RemoveField(model_name='workspaceschedule', name='fyle_job_id'),
        migrations.AddField(model_name='workspaceschedule', name='schedule', field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to='django_q.Schedule')),
        migrations.AddField(
            model_name='workspaceschedule', name='workspace', field=models.OneToOneField(default=1, help_text='Reference to Workspace model', on_delete=django.db.models.deletion.PROTECT, to='workspaces.Workspace'), preserve_default=False
        ),
        migrations.DeleteModel(name='WorkspaceSettings'),
    ]
