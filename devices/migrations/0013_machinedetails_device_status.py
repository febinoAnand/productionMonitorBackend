# Generated by Django 4.2.4 on 2024-10-08 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0012_alter_shifttiming_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='machinedetails',
            name='device_status',
            field=models.IntegerField(default=1),
        ),
    ]
