# Generated by Django 4.2.4 on 2024-07-18 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0003_delete_machine_machinegroup_machine_list_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='machinedetails',
            name='machine_name',
            field=models.CharField(default='none', max_length=45),
        ),
    ]
