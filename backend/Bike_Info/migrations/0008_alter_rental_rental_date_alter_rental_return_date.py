# Generated by Django 4.2.1 on 2023-07-08 20:48

from django.db import migrations, models
from datetime import datetime

class Migration(migrations.Migration):

    dependencies = [
        ('Bike_Info', '0007_rename_km_later_bike_info_km_now'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rental',
            name='rental_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='rental',
            name='return_date',
            field=models.DateTimeField(auto_now_add=True, default=datetime(2023, 1, 1)),
            preserve_default=False,
        ),
    ]
