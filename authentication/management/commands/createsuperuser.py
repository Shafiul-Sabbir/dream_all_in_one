from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand
from django.core.management import CommandError
from django.core.management.base import CommandParser
from getpass import getpass

class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser):
        super().add_arguments(parser)
        parser.add_argument('--primary_phone', type=str, help='Primary phone number')

    def handle(self, *args, **options):
        primary_phone = options.get('primary_phone')

        if not primary_phone:
            # Prompt for phone if not provided
            primary_phone = input('Primary phone: ')

        options['primary_phone'] = primary_phone

        super().handle(*args, **options)
