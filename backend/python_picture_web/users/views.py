# from .models import Users
# from django.shortcuts import HttpResponse

# #Create your views here.

# def authorization(request):
#     if request.GET:
#         users = Users.objects.all()
#         login = request.GET.get("login")
#         password = request.GET.get("password")
#         for _user in users:
#             if _user.login == login and _user.password == password:
#                 key = _user.key
#                 _user.authorization = True
#                 _user.save(update_fields=["authorization"])
#                 return HttpResponse(key)
#             elif _user.password != password:
#                 return HttpResponse("Incorrect password.", status=404)
#             else:
#                 return HttpResponse("User not found.", status=404)

from users.models import Users
from django.shortcuts import HttpResponse

def authorization(request):
    if request.GET:
        login = request.GET.get("login")
        password = request.GET.get("password")

        try:
            # Попытка найти пользователя по логину и паролю
            user = Users.objects.get(login=login, password=password)
            if user.authorization:
                # Если пользователь авторизован, возвращаем его ключ
                return HttpResponse(user.key)
            else:
                # Если пользователь не авторизован, возвращаем ошибку
                return HttpResponse("Unauthorized", status=401)
        except Users.DoesNotExist:
            # Если пользователь не найден, возвращаем ошибку
            return HttpResponse("User not found", status=404)


