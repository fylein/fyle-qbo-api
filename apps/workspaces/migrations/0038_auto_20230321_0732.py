# Generated by Django 3.1.14 on 2023-03-21 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('workspaces', '0037_auto_20230125_0735')]

    operations = [migrations.AlterField(model_name='workspacegeneralsettings', name='is_simplify_report_closure_enabled', field=models.BooleanField(default=True, help_text='Simplify report closure is enabled'))]
