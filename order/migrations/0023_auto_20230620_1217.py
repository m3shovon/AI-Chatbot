# Generated by Django 3.2.4 on 2023-06-20 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0022_measurement_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='measurement',
            name='Measurement_body',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='measurement',
            name='Measurement_dress',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='measurement',
            name='Sleeve_less',
            field=models.BooleanField(default=False),
        ),
    ]
