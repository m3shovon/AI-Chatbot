# Generated by Django 3.2.4 on 2024-10-21 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userlog', '0006_auto_20241020_1226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlog',
            name='action',
            field=models.CharField(max_length=2550),
        ),
    ]
