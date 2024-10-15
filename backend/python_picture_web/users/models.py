from django.db import models

# Create your models here.
class Users(models.Model):
    login = models.CharField('login', max_length=32)
    password = models.CharField('login', max_length=32)
    key = models.IntegerField('key')
    authorization = models.BooleanField('authorization')

    def __str__(self):
        return self.login
