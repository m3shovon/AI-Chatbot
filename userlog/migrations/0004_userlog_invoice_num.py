# Generated by Django 3.2.4 on 2023-05-04 06:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0022_measurement_service'),
        ('userlog', '0003_userlog_action_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlog',
            name='invoice_num',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='order.invoice'),
        ),
    ]
