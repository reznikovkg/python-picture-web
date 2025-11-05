# from django.core.management.base import BaseCommand
# from users.models import Users

# class Command(BaseCommand):
#     help = 'Update user role and authorization'

#     def add_arguments(self, parser):
#         parser.add_argument('login', type=str, help='Login of the user to update')
#         parser.add_argument('role', type=str, help='New role for the user')
#         parser.add_argument('authorization', type=bool, help='New authorization status for the user')

#     def handle(self, *args, **options):
#         login = options['login']
#         role = options['role']
#         authorization = options['authorization']

#         try:
#             user = Users.objects.get(login=login)
#             user.role = role
#             user.authorization = authorization
#             user.save()      
#             #Users.objects.filter(login__in=login).update(role=user.role ,authorization=user.authorization)
#             #Users.objects.
#             self.stdout.write(self.style.SUCCESS(f'Successfully updated user: {login}'))
#         except Users.DoesNotExist:
#             self.stdout.write(self.style.ERROR(f'User with login {login} does not exist.'))

from django.core.management.base import BaseCommand
from users.models import Users

class Command(BaseCommand):
    help = 'Update user role and authorization'

    def add_arguments(self, parser):
        parser.add_argument('login', type=str, help='Login of the user to update')
        parser.add_argument('password', type=str, help='New password of the user to update')
        parser.add_argument('role', type=str, help='New role for the user')
        parser.add_argument('authorization', type=bool, help='New authorization status for the user')

    def handle(self, *args, **options):
        login = options['login']
        password = options['password']
        role = options['role']
        authorization = options['authorization']

        try:
            user = Users.objects.get(login=login)
            user.role = role
            user.authorization = authorization
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated user: {login}'))
        except Users.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with login {login} does not exist.'))