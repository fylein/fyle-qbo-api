# Generated by Django 3.2.14 on 2024-11-18 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0046_workspacegeneralsettings_import_code_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workspacegeneralsettings',
            name='change_accounting_period',
            field=models.BooleanField(default=True, help_text='Export Expense when accounting period is closed'),
        ),
    ]
