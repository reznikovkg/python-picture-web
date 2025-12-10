from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Users
import logging
import secrets
import string

logger = logging.getLogger(__name__)

def generate_user_key(length=32):
    """Генерация уникального ключа для пользователя"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def check_admin_access(user_key):
    """Проверка что пользователь является администратором"""
    try:
        user = Users.objects.get(key=user_key)
        return user.role == 'admin' and user.authorization
    except Users.DoesNotExist:
        return False

@csrf_exempt
def auth_view(request):
    login = request.GET.get('login')
    password = request.GET.get('password')
    
    try:
        # наличие пользователя в базе данных
        user = Users.objects.get(login=login, password=password)
        # разрешён ли пользователю вход
        if user.authorization:
            return JsonResponse({
                'key': user.key,
                'login': user.login,
                'role': user.role,
                'authorization': user.authorization,
                'email': user.email or ''  # добавление email
            })
        else:
            return JsonResponse({"error": "Not authorized"}, status=403)
            
    except Users.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

@csrf_exempt
def users_list(request, key):
    """Получение списка всех пользователей (только для администратора)"""
    if request.method == "GET":
        # права доступа
        if not check_admin_access(key):
            return JsonResponse({"error": "Доступ запрещен. Требуются права администратора."}, status=403)
        
        try:
            users = Users.objects.all().order_by('login')
            users_data = []
            
            for user in users:
                users_data.append({
                    'id': user.id,
                    'login': user.login,
                    'email': user.email or '',
                    'role': user.role,
                    'authorization': user.authorization,
                    'key': user.key
                })
            
            return JsonResponse({
                'success': True,
                'users': users_data
            })
            
        except Exception as e:
            logger.error(f"Error fetching users: {str(e)}")
            return JsonResponse({"error": "Ошибка при получении списка пользователей"}, status=500)
    
    return JsonResponse({"error": "Метод не поддерживается"}, status=405)

@csrf_exempt
def create_user(request, key):
    """Создание нового пользователя (только для администратора)"""
    if request.method == "POST":
        # права доступа
        if not check_admin_access(key):
            return JsonResponse({"error": "Доступ запрещен. Требуются права администратора."}, status=403)
        
        try:
            import json
            data = json.loads(request.body.decode('utf-8'))
            
            login = data.get('login')
            password = data.get('password')
            email = data.get('email', '')
            role = data.get('role', 'regular')
            
            # валидация данных
            if not all([login, password]):
                return JsonResponse({"error": "Логин и пароль обязательны"}, status=400)
            
            # проверка что роль валидна и не админ
            if role not in ['moderator', 'regular']:
                return JsonResponse({"error": "Недопустимая роль. Разрешены только moderator и regular"}, status=400)
            
            # проверка уникальность логина
            if Users.objects.filter(login=login).exists():
                return JsonResponse({"error": "Пользователь с таким логином уже существует"}, status=400)
            
            # генерация уникальный ключ
            user_key = generate_user_key()
            while Users.objects.filter(key=user_key).exists():
                user_key = generate_user_key()
            
            # создание пользователя
            user = Users.objects.create(
                login=login,
                password=password,
                key=user_key,
                role=role,
                authorization=True,  # пользователи (новые) по умолчанию авторизованы
                email=email
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Пользователь успешно создан',
                'user': {
                    'id': user.id,
                    'login': user.login,
                    'email': user.email or '',
                    'role': user.role,
                    'authorization': user.authorization,
                    'key': user.key
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Неверный формат JSON"}, status=400)
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return JsonResponse({"error": "Ошибка при создании пользователя"}, status=500)
    
    return JsonResponse({"error": "Метод не поддерживается"}, status=405)

@csrf_exempt
def update_user(request, key, user_id):
    """Редактирование пользователя (только для администратора)"""
    if request.method == "PUT":
        # права доступа
        if not check_admin_access(key):
            return JsonResponse({"error": "Доступ запрещен. Требуются права администратора."}, status=403)
        
        try:
            import json
            data = json.loads(request.body.decode('utf-8'))
            
            # получение пользователя для редактирования
            try:
                user_to_edit = Users.objects.get(id=user_id)
            except Users.DoesNotExist:
                return JsonResponse({"error": "Пользователь не найден"}, status=404)
            
            # нельзя редактировать самого себя (чтобы админ случайно не понизил себя)
            current_user = Users.objects.get(key=key)
            if user_to_edit.id == current_user.id:
                return JsonResponse({"error": "Нельзя редактировать собственный аккаунт"}, status=400)
            
            login = data.get('login')
            password = data.get('password')
            email = data.get('email', '')
            role = data.get('role')
            authorization = data.get('authorization')
            
            # обновление поля если они переданы
            if login is not None:
                # уникальность логина (кроме текущего пользователя)
                if Users.objects.filter(login=login).exclude(id=user_id).exists():
                    return JsonResponse({"error": "Пользователь с таким логином уже существует"}, status=400)
                user_to_edit.login = login
            
            if password is not None:
                user_to_edit.password = password
            
            if email is not None:
                user_to_edit.email = email
            
            if role is not None:
                if role not in ['moderator', 'regular']:
                    return JsonResponse({"error": "Недопустимая роль. Разрешены только moderator и regular"}, status=400)
                user_to_edit.role = role
            
            if authorization is not None:
                user_to_edit.authorization = authorization
            
            user_to_edit.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Пользователь успешно обновлен',
                'user': {
                    'id': user_to_edit.id,
                    'login': user_to_edit.login,
                    'email': user_to_edit.email or '',
                    'role': user_to_edit.role,
                    'authorization': user_to_edit.authorization,
                    'key': user_to_edit.key
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Неверный формат JSON"}, status=400)
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return JsonResponse({"error": "Ошибка при обновлении пользователя"}, status=500)
    
    return JsonResponse({"error": "Метод не поддерживается"}, status=405)

@csrf_exempt
def delete_user(request, key, user_id):
    """Удаление пользователя (только для администратора)"""
    if request.method == "DELETE":
        # проверка прав доступа
        if not check_admin_access(key):
            return JsonResponse({"error": "Доступ запрещен. Требуются права администратора."}, status=403)
        
        try:
            # получение пользователя для удаления
            try:
                user_to_delete = Users.objects.get(id=user_id)
            except Users.DoesNotExist:
                return JsonResponse({"error": "Пользователь не найден"}, status=404)
            
            # нельзя удалить самого себя
            current_user = Users.objects.get(key=key)
            if user_to_delete.id == current_user.id:
                return JsonResponse({"error": "Нельзя удалить собственный аккаунт"}, status=400)
            
            # нельзя удалить последнего администратора
            if user_to_delete.role == 'admin':
                admin_count = Users.objects.filter(role='admin', authorization=True).count()
                if admin_count <= 1:
                    return JsonResponse({"error": "Нельзя удалить последнего администратора"}, status=400)
            
            # удалить пользователя
            user_to_delete.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Пользователь успешно удален'
            })
            
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return JsonResponse({"error": "Ошибка при удалении пользователя"}, status=500)
    
    return JsonResponse({"error": "Метод не поддерживается"}, status=405)

@csrf_exempt
def get_current_user(request, key):
    """Получение информации о текущем пользователе"""
    if request.method == "GET":
        try:
            user = Users.objects.get(key=key)
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'login': user.login,
                    'email': user.email or '',
                    'role': user.role,
                    'authorization': user.authorization
                }
            })
        except Users.DoesNotExist:
            return JsonResponse({"error": "Пользователь не найден"}, status=404)
    
    return JsonResponse({"error": "Метод не поддерживается"}, status=405)
