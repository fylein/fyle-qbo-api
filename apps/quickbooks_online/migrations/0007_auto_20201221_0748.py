# Generated by Django 3.0.3 on 2020-12-21 07:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('quickbooks_online', '0006_auto_20201120_0718')]

    operations = [
        migrations.AlterModelTable(name='bill', table='bills'),
        migrations.AlterModelTable(name='billlineitem', table='bill_lineitems'),
        migrations.AlterModelTable(name='cheque', table='cheques'),
        migrations.AlterModelTable(name='chequelineitem', table='cheque_lineitems'),
        migrations.AlterModelTable(name='creditcardpurchase', table='credit_card_purchases'),
        migrations.AlterModelTable(name='creditcardpurchaselineitem', table='credit_card_purchase_lineitems'),
        migrations.AlterModelTable(name='journalentry', table='journal_entries'),
        migrations.AlterModelTable(name='journalentrylineitem', table='journal_entry_lineitems'),
    ]
