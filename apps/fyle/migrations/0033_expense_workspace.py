# Generated by Django 3.1.14 on 2023-09-05 12:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0042_workspacegeneralsettings_name_in_journal_entry'),
        ('fyle', '0032_expense_accounting_export_summary'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='workspace',
            field=models.ForeignKey(help_text='To which workspace this expense belongs to', null=True, on_delete=django.db.models.deletion.PROTECT, to='workspaces.workspace'),
        ),
    ]