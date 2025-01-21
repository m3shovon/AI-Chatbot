# Generated by Django 3.2.4 on 2024-09-10 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0024_alter_pettycash_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalvoucher',
            name='is_payment_voucher',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='journalvoucher',
            name='is_receive_voucher',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='journalvoucheritems',
            name='is_printable',
            field=models.BooleanField(default=False),
        ),
    ]
