# Generated by Django 4.2.1 on 2023-07-08 16:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Bike_Info', '0006_rename_km_bike_info_km_later_bike_info_km_previous'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bike_info',
            old_name='KM_Later',
            new_name='KM_Now',
        ),
    ]
