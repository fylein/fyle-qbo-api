# Generated by Django 3.1.14 on 2022-07-14 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_auto_20220406_1142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='error',
            name='type',
            field=models.CharField(choices=[('EMPLOYEE_MAPPING', 'EMPLOYEE_MAPPING'), ('CATEGORY_MAPPING', 'CATEGORY_MAPPING'), ('TAX_MAPPING', 'TAX_MAPPING'), ('QBO_ERROR', 'QBO_ERROR')], help_text='Error type', max_length=50),
        ),
    ]