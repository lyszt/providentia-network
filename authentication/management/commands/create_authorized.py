import base64
import os

from django.core.management.base import BaseCommand, CommandError
from authentication.models import AuthorizedApps

class Command(BaseCommand):
    help = 'Create an authorized application entry in the database'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str, help='Name of the application')

    def handle(self, *args, **options):
        app_name = options['app_name']

        if AuthorizedApps.objects.filter(app_name=app_name).exists():
            raise CommandError(f'Application with name "{app_name}" already exists.')

        api_key = os.urandom(16)
        api_key = base64.urlsafe_b64encode(api_key).decode('utf-8')
        authorized_app = AuthorizedApps(app_name=app_name, api_key=api_key)
        authorized_app.save()
        self.stdout.write(self.style.SUCCESS(f'Successfully added app "{app_name}" with API key: {api_key}'))