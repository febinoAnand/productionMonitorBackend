# Generated by Django 4.2.4 on 2024-09-25 09:25

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashbaordData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now=True)),
                ('time', models.TimeField(auto_now=True)),
                ('dashbaordData', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='LogData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('received_data', models.CharField(blank=True, max_length=2000, null=True)),
                ('protocol', models.CharField(blank=True, max_length=15, null=True)),
                ('topic_api', models.CharField(blank=True, max_length=100, null=True)),
                ('data_id', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductionData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('shift_number', models.IntegerField(null=True)),
                ('shift_name', models.CharField(blank=True, max_length=45, null=True)),
                ('target_production', models.IntegerField()),
                ('machine_id', models.CharField(max_length=45)),
                ('machine_name', models.CharField(max_length=45)),
                ('production_count', models.IntegerField()),
                ('production_date', models.DateField(null=True)),
                ('log_data_id', models.IntegerField()),
                ('timestamp', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductionUpdateData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField(auto_now=True)),
                ('production_data', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='RawData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('data', models.TextField()),
                ('date', models.DateField(blank=True, null=True)),
                ('time', models.TimeField(blank=True, null=True)),
                ('deviceID', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='devices.devicedetails')),
                ('eventGroupID', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='events.eventgroup')),
                ('eventID', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='events.event')),
                ('machineID', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='devices.machinedetails')),
            ],
        ),
        migrations.CreateModel(
            name='ProblemData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('issueTime', models.DateTimeField()),
                ('acknowledgeTime', models.DateTimeField(blank=True, null=True)),
                ('endTime', models.DateTimeField(blank=True, null=True)),
                ('dateTimeNow', models.DateTimeField(auto_now=True)),
                ('deviceID', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='devices.devicedetails')),
                ('eventGroupID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.eventgroup')),
                ('eventID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
                ('machineID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='devices.machinedetails')),
                ('rfidTime', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='devices.rfid')),
            ],
        ),
        migrations.CreateModel(
            name='MachineData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('data', models.JSONField()),
                ('create_date_time', models.DateTimeField(auto_now_add=True)),
                ('update_date_time', models.DateTimeField(auto_now=True)),
                ('timestamp', models.CharField(max_length=50, null=True)),
                ('device_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='devices.devicedetails')),
                ('log_data_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.logdata')),
                ('machine_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='devices.machinedetails')),
            ],
        ),
        migrations.CreateModel(
            name='LastProblemData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('issueTime', models.DateTimeField(blank=True, null=True)),
                ('acknowledgeTime', models.DateTimeField(blank=True, null=True)),
                ('endTime', models.DateTimeField(blank=True, null=True)),
                ('dateTimeNow', models.DateTimeField(auto_now_add=True)),
                ('deviceID', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='devices.devicedetails')),
                ('eventGroupID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.eventgroup')),
                ('eventID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
                ('machineID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='devices.machinedetails')),
                ('rfidTime', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='devices.rfid')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('data', models.JSONField()),
                ('protocol', models.CharField(blank=True, max_length=10, null=True)),
                ('topic_api', models.CharField(blank=True, max_length=100, null=True)),
                ('create_date_time', models.DateTimeField(auto_now_add=True)),
                ('update_date_time', models.DateTimeField(auto_now=True)),
                ('timestamp', models.CharField(max_length=50, null=True)),
                ('device_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='devices.devicedetails')),
                ('log_data_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.logdata')),
            ],
        ),
    ]
