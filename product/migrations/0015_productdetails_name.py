# Generated by Django 3.2.4 on 2023-05-10 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0014_auto_20230327_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='productdetails',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
