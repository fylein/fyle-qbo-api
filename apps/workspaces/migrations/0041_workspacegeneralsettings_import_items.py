# Generated by Django 3.1.14 on 2023-04-22 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('workspaces', '0040_workspacegeneralsettings_is_multi_currency_allowed')]

    operations = [migrations.AddField(model_name='workspacegeneralsettings', name='import_items', field=models.BooleanField(default=False, help_text='Auto import Items to Fyle'))]
