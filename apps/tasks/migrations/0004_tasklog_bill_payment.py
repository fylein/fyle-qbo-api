# Generated by Django 3.0.3 on 2021-01-20 18:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [('quickbooks_online', '0008_auto_20210120_1831'), ('tasks', '0003_auto_20201221_0748')]

    operations = [migrations.AddField(model_name='tasklog', name='bill_payment', field=models.ForeignKey(help_text='Reference to BillPayment', null=True, on_delete=django.db.models.deletion.PROTECT, to='quickbooks_online.BillPayment'))]
