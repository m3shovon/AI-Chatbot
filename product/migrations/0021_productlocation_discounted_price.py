# Generated by Django 3.2.4 on 2023-10-25 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0020_auto_20230829_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='productlocation',
            name='discounted_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20),
        ),
    ]
