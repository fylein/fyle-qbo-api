# Generated by Django 3.1.14 on 2022-04-12 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('workspaces', '0027_workspace_onboarding_state')]

    operations = [migrations.AddField(model_name='workspacegeneralsettings', name='import_vendors_as_merchants', field=models.BooleanField(default=False, help_text='Auto import vendors from qbo as merchants to Fyle'))]
