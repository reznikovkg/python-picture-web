from django.core.management.base import BaseCommand
from users.models import Users

class Command(BaseCommand):
    help = 'Update authorization for specific users'

    def add_arguments(self, parser):
        parser.add_argument('logins', nargs='+', type=str, help='List of user logins to update')

    def handle(self, *args, **options):
        logins = options['logins']
        Users.objects.filter(login__in=logins).update(authorization=True)
        self.stdout.write(self.style.SUCCESS(f'Successfully updated authorization for users: {", ".join(logins)}'))