# Generated by Django 4.2.4 on 2024-08-23 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0006_mqttsettings_pub_topic_mqttsettings_sub_topic'),
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enable_printing', models.BooleanField(default=False)),
            ],
        ),
    ]