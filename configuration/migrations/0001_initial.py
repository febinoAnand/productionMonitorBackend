# Generated by Django 4.2.4 on 2024-07-16 07:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MQTT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(max_length=50)),
                ('port', models.IntegerField()),
                ('username', models.CharField(max_length=40)),
                ('password', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('portname', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UART',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('baudrate', models.IntegerField(choices=[(9600, '9600'), (115200, '115200')])),
                ('parity', models.CharField(choices=[('none', 'None'), ('odd', 'Odd'), ('even', 'Even')], max_length=10)),
                ('databit', models.IntegerField(choices=[(5, '5'), (6, '6'), (7, '7'), (8, '8')])),
                ('stopbit', models.DecimalField(choices=[(1.0, '1'), (1.5, '1.5'), (2.0, '2')], decimal_places=1, max_digits=4)),
                ('CTS', models.BooleanField()),
                ('DTR', models.BooleanField()),
                ('XON', models.BooleanField()),
                ('comport', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='configuration.port')),
            ],
        ),
    ]
