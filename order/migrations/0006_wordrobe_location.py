# Generated by Django 3.2.4 on 2021-12-27 15:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_auto_20211219_1512'),
        ('order', '0005_auto_20211223_1902'),
    ]

    operations = [
        migrations.AddField(
            model_name='wordrobe',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.warehouse'),
        ),
    ]
