# Generated by Django 4.0 on 2024-01-31 13:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_alter_productlocation_attributes'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductLocationEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('ProductLocation', models.ManyToManyField(blank=True, related_name='ProductLocation', related_query_name='ProductLocation', to='product.ProductLocation')),
            ],
        ),
    ]
