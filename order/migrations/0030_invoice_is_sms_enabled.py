# Generated by Django 3.2.4 on 2023-09-24 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0029_measurement_gown_bottom'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='is_sms_enabled',
            field=models.BooleanField(default=True),
        ),
    ]
