# Generated by Django 3.1.14 on 2023-08-01 12:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fyle', '0030_expense_posted_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='expensefilter',
            options={'ordering': ['rank']},
        ),
    ]
