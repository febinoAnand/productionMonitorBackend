# Generated by Django 4.2.4 on 2024-10-09 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0012_alter_shifttiming_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicedetails',
            name='device_status',
            field=models.IntegerField(default=1),
        ),
    ]
