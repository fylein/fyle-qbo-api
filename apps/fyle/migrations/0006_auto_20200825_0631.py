# Generated by Django 3.0.3 on 2020-08-25 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('fyle', '0005_auto_20200819_1419')]

    operations = [
        migrations.RemoveField(model_name='expensegroupsettings', name='export_date'),
        migrations.AddField(model_name='expensegroupsettings', name='export_date_type', field=models.CharField(default='current_date', help_text='Export Date', max_length=100)),
    ]
