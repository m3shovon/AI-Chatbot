# Generated by Django 3.2.4 on 2023-06-26 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrm', '0006_auto_20230411_2022'),
    ]

    operations = [
        migrations.AddField(
            model_name='payslip',
            name='manual_adjustment',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]
