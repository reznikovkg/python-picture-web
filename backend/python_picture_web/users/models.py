from django.db import models

ROLES_CHOICES = (
    ('admin', 'Администратор'),
    ('moderator', 'Модератор'),
    ('regular', 'Обычный пользователь'),
)

class Users(models.Model):
    login = models.CharField('login', max_length=32)
    password = models.CharField('password', max_length=32)
    key = models.CharField('key', max_length=32)
    role = models.CharField('role', choices=ROLES_CHOICES, default='regular', max_length=10)
    authorization = models.BooleanField('authorization', default=False)
    email = models.EmailField('email', max_length=254, blank=True, null=True)  # поле для email (null - для совместимости с текущими тестовыми данными)
    
    class Meta:
        db_table = 'user_user'
    
    def __str__(self):
        return self.login
