# Generated by Django 3.1.13 on 2022-01-25 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0020_fylecredential_cluster_domain'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspaceschedule',
            name='total_errors',
            field=models.IntegerField(help_text='Total Number of error occured after schedule run', null=True),
        ),
    ]