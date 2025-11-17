from django.contrib import admin
from .models import Users

class UsersAdmin(admin.ModelAdmin):
    list_display = ('login', 'role', 'authorization') # отображение в списке
    search_fields = ('login', 'role')                 # поиск
    list_filter = ('role', 'authorization')           # фильтры
    ordering = ('login',)                             # сортировка по имени пользователя

# Register your models here.
admin.site.register(Users)