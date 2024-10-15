from django.core.management import BaseCommand
from django.core.management import call_command
from configuration.models import Setting
import os


class Command(BaseCommand):
    help = 'Initialize data for Project'

    def handle(self, *args, **kwargs):
        if not Setting.objects.exists():
            env = os.getenv('ENV', 'local')
            if env == 'production':
                call_command('loaddata', 'initial_data.json')
                self.stdout.write(self.style.SUCCESS('Loaded production fixture'))
            else:
                call_command('loaddata', 'initial_local_data.json')
                self.stdout.write(self.style.SUCCESS('Loaded local fixture'))
                