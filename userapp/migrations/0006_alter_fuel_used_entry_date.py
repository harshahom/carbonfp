# Generated by Django 4.2.6 on 2023-11-28 09:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0005_alter_fuel_used_entry_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuel_used',
            name='entry_date',
            field=models.DateField(default=datetime.date(2023, 11, 28)),
        ),
    ]
