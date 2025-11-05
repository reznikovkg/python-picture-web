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

# from users.models import Users
# from django.shortcuts import HttpResponse

# def authorization(request):
#     if request.GET:
#         login = request.GET.get("login")
#         password = request.GET.get("password")

#         try:
#             # Попытка найти пользователя по логину и паролю
#             user = Users.objects.get(login=login, password=password)
#             if user.authorization:
#                 # Если пользователь авторизован, возвращаем его ключ
#                 return HttpResponse(user.key)
#             else:
#                 # Если пользователь не авторизован, возвращаем ошибку
#                 return HttpResponse("Unauthorized", status=401)
#         except Users.DoesNotExist:
#             # Если пользователь не найден, возвращаем ошибку
#             return HttpResponse("User not found", status=404)

# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Users
# import logging

# logger = logging.getLogger(__name__)

# @csrf_exempt
# def auth_view(request):
#     try:
#         if request.method == 'GET':
#             login = request.GET.get('login', '').strip()
#             password = request.GET.get('password', '').strip()
#         else:
#             return JsonResponse({'error': 'Method not allowed'}, status=405)
        
#         # Ищем пользователя
#         try:
#             user = Users.objects.get(login=login)
            
#             # Проверяем пароль
#             if user.password != password:
#                 return JsonResponse({'error': 'Invalid password'}, status=401)
            
#             # Проверяем авторизацию
#             if not user.authorization:
#                 return JsonResponse({'error': 'User not authorized'}, status=403)
            
#             # Успешная авторизация
#             return JsonResponse({
#                 'token': user.key,
#                 'login': user.login,
#                 'role': user.role
#             })
            
#         except Users.DoesNotExist:
#             return JsonResponse({'error': 'User not found'}, status=404)
            
#     except Exception as e:
#         logger.error(f"Auth error: {str(e)}")
#         return JsonResponse({'error': 'Server error'}, status=500)

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Users
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
# def auth_view(request):
#     try:
#         if request.method == 'GET':
#             login = request.GET.get('login', '').strip()
#             password = request.GET.get('password', '').strip()
#         else:
#             return HttpResponse('Method not allowed', status=405)

#         try:
#             user = Users.objects.get(login=login, password=password)
#             if user.password != password:
#                 return HttpResponse('Invalid password', status=401)

#             if not user.authorization:
#                 return HttpResponse('User not authorized', status=403)

#             # Возвращаем просто строку - токен
#             return HttpResponse(user.key)

#         except Users.DoesNotExist:
#             return HttpResponse('User not found', status=404)

#     except Exception as e:
#         logger.error(f"Auth error: {str(e)}")
#         return HttpResponse('Server error', status=500)

def auth_view(request):
    login = request.GET.get('login')
    password = request.GET.get('password')
    
    try:
        # Ищем пользователя в базе данных
        user = Users.objects.get(login=login, password=password)
        
        # Проверяем, разрешён ли ему вход
        if user.authorization:
            return HttpResponse(user.key)  # Возвращаем токен
        else:
            return HttpResponse("Not authorized", status=403)
            
    except Users.DoesNotExist:
        return HttpResponse("User not found", status=404)