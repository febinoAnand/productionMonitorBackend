# Generated by Django 4.2.4 on 2024-07-19 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0004_mqttsettings_keepalive_alter_mqttsettings_qos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mqttsettings',
            name='password',
            field=models.CharField(blank=True, max_length=45),
        ),
        migrations.AlterField(
            model_name='mqttsettings',
            name='username',
            field=models.CharField(blank=True, max_length=45),
        ),
    ]
