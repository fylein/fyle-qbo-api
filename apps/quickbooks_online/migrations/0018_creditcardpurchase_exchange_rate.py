# Generated by Django 3.2.14 on 2024-12-06 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickbooks_online', '0017_journalentry_exchange_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditcardpurchase',
            name='exchange_rate',
            field=models.FloatField(help_text='Exchange rate', null=True),
        ),
    ]
