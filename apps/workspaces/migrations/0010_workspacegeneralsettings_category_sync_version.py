# Generated by Django 3.0.3 on 2021-02-22 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('workspaces', '0009_workspacegeneralsettings_auto_map_employees')]

    operations = [migrations.AddField(model_name='workspacegeneralsettings', name='category_sync_version', field=models.CharField(default='v1', help_text='Category sync version', max_length=50))]
