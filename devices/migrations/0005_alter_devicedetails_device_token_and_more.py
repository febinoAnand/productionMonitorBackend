# Generated by Django 4.2.4 on 2024-07-20 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0004_machinedetails_machine_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicedetails',
            name='device_token',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='devicedetails',
            name='protocol',
            field=models.CharField(choices=[('mqtt', 'MQTT'), ('http', 'HTTP')], max_length=10),
        ),
        migrations.AlterField(
            model_name='machinedetails',
            name='machine_id',
            field=models.CharField(max_length=15, unique=True),
        ),
    ]
