# Generated by Django 5.1.5 on 2025-04-17 00:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_userpreferences'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='deadline',
            field=models.DateField(default=datetime.date(2025, 4, 19)),
        ),
    ]
