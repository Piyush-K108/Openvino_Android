# Generated by Django 4.2.1 on 2023-06-13 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_rename_is_admin_useraccounts_is_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccounts',
            name='otp',
            field=models.CharField(max_length=6, null=True),
        ),
    ]
