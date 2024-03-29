# Generated by Django 3.1.14 on 2022-03-23 09:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [('workspaces', '0025_workspace_fyle_currency')]

    operations = [
        migrations.AlterField(model_name='workspacegeneralsettings', name='reimbursable_expenses_object', field=models.CharField(help_text='Reimbursable Expenses type', max_length=50, null=True)),
        migrations.AlterField(
            model_name='workspacegeneralsettings',
            name='workspace',
            field=models.OneToOneField(help_text='Reference to Workspace model', on_delete=django.db.models.deletion.PROTECT, related_name='workspace_general_settings', to='workspaces.workspace'),
        ),
        migrations.AlterField(
            model_name='workspaceschedule', name='workspace', field=models.OneToOneField(help_text='Reference to Workspace model', on_delete=django.db.models.deletion.PROTECT, related_name='workspace_schedules', to='workspaces.workspace')
        ),
    ]
