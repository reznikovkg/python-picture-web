from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Users
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def auth_view(request):
    login = request.GET.get('login')
    password = request.GET.get('password')
    
    try:
        # Ищем пользователя в базе данных
        user = Users.objects.get(login=login, password=password)
        # Проверяем, разрешён ли ему вход
        if user.authorization:
            return JsonResponse({
                'key': user.key,
                'login': user.login,
                'role': user.role,
                'authorization': user.authorization
            })
            #return HttpResponse(user.key)  # Возвращаем токен
        else:
            return JsonResponse({"error": "Not authorized"}, status=403)
            #return HttpResponse("Not authorized", status=403)
            
    except Users.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
        #return HttpResponse("User not found", status=404)