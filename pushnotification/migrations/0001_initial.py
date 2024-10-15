# Generated by Django 4.2.4 on 2024-10-11 21:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        # ('auth', '0013_alter_user_email'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_name', models.CharField(max_length=30)),
                ('application_id', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SendReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('title', models.CharField(max_length=25)),
                ('message', models.TextField(max_length=200)),
                ('delivery_status', models.CharField(default='-', max_length=50)),
                ('send_to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notify_user', to=settings.AUTH_USER_MODEL)),
                ('users_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_group', to='auth.group')),
            ],
        ),
        migrations.CreateModel(
            name='NotificationAuth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('noti_token', models.CharField(max_length=50)),
                ('user_to_auth', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_name', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
