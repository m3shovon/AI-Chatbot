# Generated by Django 4.0 on 2023-08-08 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrm', '0004_alter_payslip_payment_method_info_1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payslip',
            name='payment_method_info_1',
            field=models.TextField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payslip',
            name='payment_method_info_2',
            field=models.TextField(default=0),
            preserve_default=False,
        ),
    ]
