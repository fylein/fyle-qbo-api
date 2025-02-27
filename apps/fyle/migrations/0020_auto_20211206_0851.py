# Generated by Django 3.1.13 on 2021-12-06 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('fyle', '0019_auto_20211108_0422')]

    operations = [
        migrations.AlterField(model_name='expense', name='custom_properties', field=models.JSONField(null=True)),
        migrations.AlterField(model_name='expensegroup', name='description', field=models.JSONField(help_text='Description', max_length=255, null=True)),
        migrations.AlterField(model_name='expensegroup', name='response_logs', field=models.JSONField(help_text='Reponse log of the export', null=True)),
    ]
