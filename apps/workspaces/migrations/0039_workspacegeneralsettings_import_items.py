# Generated by Django 3.1.14 on 2023-04-11 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0038_auto_20230321_0732'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspacegeneralsettings',
            name='import_items',
            field=models.BooleanField(default=False, help_text='Auto import Items to Fyle'),
        ),
    ]