# Generated by Django 3.2.4 on 2021-12-25 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrm', '0002_auto_20211225_0614'),
    ]

    operations = [
        migrations.AddField(
            model_name='payslip',
            name='due',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AddField(
            model_name='payslip',
            name='payment',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]
