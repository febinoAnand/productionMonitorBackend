# Generated by Django 4.2.4 on 2024-09-28 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0010_alter_shifttiming_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='shifttiming',
            name='start_hours',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
