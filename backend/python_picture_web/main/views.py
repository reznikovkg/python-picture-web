from django.http import JsonResponse
from django.shortcuts import HttpResponse
from .models import Analyse
from users.models import Users
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from datetime import datetime
import os
import json
import requests

from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from image_classifier.main.run import MainImageClassifierBySkinLesion

def check_user_access(user, analyse=None):
    """Проверка прав доступа пользователя к анализу"""
    if user.role in ['admin', 'moderator']:
        return True
    if analyse and analyse.user_key == user:
        return True
    return False

def get_analyses_queryset(user, show_filter='active'):
    """Получение queryset анализов с учетом прав доступа и фильтра"""
    if user.role in ['admin', 'moderator']:
        analyses = Analyse.objects.all()
    else:
        analyses = Analyse.objects.filter(user_key=user)
    
    # Применяем фильтр по статусу удаления
    if show_filter == 'active':
        analyses = analyses.filter(is_deleted=False)
    elif show_filter == 'deleted':
        analyses = analyses.filter(is_deleted=True)
    # 'all' - показываем все без фильтра
    
    return analyses.order_by('-datetime')

@csrf_exempt
def cnn_result_post(request, key):
    if request.method == 'POST':
        try:
            user = Users.objects.get(key=key)
        except Users.DoesNotExist:
            return HttpResponse('Пользователь с таким ключом не найден.', status=404)

        image = request.FILES.get('image')
        if not image:
            return HttpResponse('Файл изображения обязателен.', status=400)
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%d.%m.%Y в %H:%M")
        model_1 = request.POST.get('model_1')
        model_2 = request.POST.get('model_2')
        model_3 = request.POST.get('model_3')
        ensemble = request.POST.get('ensemble')
        model_1_probability = request.POST.get('model_1_probability')
        model_2_probability = request.POST.get('model_2_probability')
        model_3_probability = request.POST.get('model_3_probability')
        ensemble_probability = request.POST.get('ensemble_probability')
        patient = request.POST.get('patient')
        description = request.POST.get('description')

        if not all([model_1, model_2, model_3, ensemble,model_1_probability, model_2_probability, model_3_probability, ensemble_probability, patient, description]):
            return HttpResponse('Отсутствуют обязательные параметры.', status=400)

        analyse = Analyse.objects.create(
            user_key=user,
            image=image,
            datetime=formatted_datetime,
            model_1=model_1,
            model_2=model_2,
            model_3=model_3,
            ensemble=ensemble,
            model_1_probability=model_1_probability,
            model_2_probability=model_2_probability,
            model_3_probability=model_3_probability,
            ensemble_probability=ensemble_probability,
            patient=patient,
            description=description,
            is_deleted=False
        )

        return JsonResponse({
            "success": True,
            "message": "Запись успешно создана.",
            "data": {
                "id": analyse.id,
                "user_key": user.key,
                "user_login": user.login,  # логин автора записи
                "image": analyse.image.url,
                "date": analyse.datetime,
                "model_1": analyse.model_1,
                "model_2": analyse.model_2,
                "model_3": analyse.model_3,
                "model_1_probability": analyse.model_1_probability,
                "model_2_probability": analyse.model_2_probability,
                "model_3_probability": analyse.model_3_probability,
                "ensemble_probability": analyse.ensemble_probability,
                "result": analyse.ensemble,
                "patient": analyse.patient,
                "description": analyse.description,
                "diagnosis": analyse.diagnosis,
                "is_deleted": analyse.is_deleted
            }
        })

    return JsonResponse({"success": False, "message": "Метод не поддерживается."}, status=405)

def cnn_results_post(request, key):
    if request.method == 'POST':
        try:
            user = Users.objects.get(key=key)
        except Users.DoesNotExist:
            return HttpResponse('Пользователь с таким ключом не найден.', status=404)

        image = request.FILES.get('image')
        if not image:
            return HttpResponse('Файл изображения обязателен.', status=400)
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%d.%m.%Y в %H:%M")
        model_1 = request.POST.get('model_1')
        model_2 = request.POST.get('model_2')
        model_3 = request.POST.get('model_3')
        ensemble = request.POST.get('ensemble')
        model_1_probability = request.POST.get('model_1_probability')
        model_2_probability = request.POST.get('model_2_probability')
        model_3_probability = request.POST.get('model_3_probability')
        ensemble_probability = request.POST.get('ensemble_probability')
        patient = request.POST.get('patient')
        description = request.POST.get('description')

        if not all([model_1, model_2, model_3, ensemble, model_1_probability, model_2_probability, model_3_probability, ensemble_probability, patient, description]):
            return HttpResponse('Отсутствуют обязательные параметры.', status=400)

        analyse = Analyse.objects.create(
            user_key=user,
            image=image,
            datetime=formatted_datetime,
            model_1=model_1,
            model_2=model_2,
            model_3=model_3,
            model_1_probability=model_1_probability,
            model_2_probability=model_2_probability,
            model_3_probability=model_3_probability,
            ensemble_probability=ensemble_probability,
            ensemble=ensemble,
            patient=patient,
            description=description,
            is_deleted=False
        )

        return JsonResponse({
            "success": True,
            "message": "Запись успешно создана.",
            "data": {
                "id": analyse.id,
                "user_key": user.key,
                "user_login": user.login,  # логин автора записи
                "image": analyse.image.url,
                "date": analyse.datetime,
                "model_1": analyse.model_1,
                "model_2": analyse.model_2,
                "model_3": analyse.model_3,
                "result": analyse.ensemble,
                "model_1_probability": record.model_1_probability,
                "model_2_probability": record.model_2_probability,
                "model_3_probability": record.model_3_probability,
                "ensemble_probability": record.ensemble_probability,
                "patient": analyse.patient,
                "description": analyse.description,
                "diagnosis": analyse.diagnosis,
                "is_deleted": analyse.is_deleted
            }
        })

    return JsonResponse({"success": False, "message": "Метод не поддерживается."}, status=405)

def get_result(request, key):
    if request.method == "GET":
        try:
            user = Users.objects.get(key=key)
        except Users.DoesNotExist:
            return HttpResponse('Пользователь с таким ключом не найден.', status=404)

        if not user.authorization:
            return HttpResponse('Доступ запрещен.', status=403)

        # Получаем параметры пагинации и фильтра
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)
        show_filter = request.GET.get('show', 'active')  # all, active, deleted

        # Получаем анализы с учетом прав и фильтра
        analyses = get_analyses_queryset(user, show_filter)

        # Пагинация
        paginator = Paginator(analyses, page_size)
        try:
            analyses_page = paginator.page(page)
        except:
            return JsonResponse({'success': False, 'message': 'Неверный номер страницы.'}, status=400)

        analyse_data = []
        for record in analyses_page:
            data = {
                "id": record.id,
                "image": record.image.url,
                "date": record.datetime,
                "model_1": record.model_1,
                "model_2": record.model_2,
                "model_3": record.model_3,
                "model_1_probability": record.model_1_probability,
                "model_2_probability": record.model_2_probability,
                "model_3_probability": record.model_3_probability,
                "ensemble_probability": record.ensemble_probability,
                "ensemble": record.ensemble,
                "patient": record.patient,
                "description": record.description,
                "diagnosis": record.diagnosis,
                "is_deleted": record.is_deleted
            }
            
            # Добавляем информацию об авторе для админа и модератора
            if user.role in ['admin', 'moderator']:
                data["author"] = record.user_key.login
                data["author_id"] = record.user_key.id
            
            analyse_data.append(data)

        return JsonResponse({
            'success': True,
            'results': analyse_data,
            'pagination': {
                'current_page': analyses_page.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_previous': analyses_page.has_previous(),
                'has_next': analyses_page.has_next(),
            }
        })

    return JsonResponse({"success": False, "message": "Метод не поддерживается."}, status=405)

def delete_row(request, key):
    if request.method == "GET":
        try:
            user = Users.objects.get(key=key)
        except Users.DoesNotExist:
            return HttpResponse('Пользователь с таким ключом не найден.', status=404)

        if not user.authorization:
            return HttpResponse('Доступ запрещен.', status=403)

        row_id = request.GET.get("id")
        permanent = request.GET.get("permanent", "false").lower() == "true"
        
        try:
            analyse = Analyse.objects.get(id=row_id)
        except Analyse.DoesNotExist:
            return HttpResponse("Анализ не найден.", status=404)

        # Проверяем права доступа
        if not check_user_access(user, analyse):
            return HttpResponse("Доступ запрещен.", status=403)

        # Для обычных пользователей - только мягкое удаление
        if user.role == 'regular':
            analyse.is_deleted = True
            analyse.save()
            return HttpResponse(True, status=200)
        
        # Для админа и модератора - выбор типа удаления
        if permanent:
            # Полное удаление с удалением файла
            if os.path.exists('python_picture_web' + str(analyse.image.url)):
                os.remove('python_picture_web' + str(analyse.image.url))
            analyse.delete()
        else:
            # Мягкое удаление
            analyse.is_deleted = True
            analyse.save()

        return HttpResponse(True, status=200)

    return JsonResponse({"success": False, "message": "Метод не поддерживается."}, status=405)

def delete_all(request, key):
    if request.method == "GET":
        try:
            user = Users.objects.get(key=key)
        except Users.DoesNotExist:
            return JsonResponse({"success": False, "message": "Пользователь с таким ключом не найден."}, status=404)

        if not user.authorization:
            return JsonResponse({"success": False, "message": "Доступ запрещен."}, status=403)

        # параметры удаления
        permanent = request.GET.get("permanent", "false").lower() == "true"
        show_filter = request.GET.get("show", "active")  # возможные значения all, active, deleted

        # queryset в зависимости от роли пользователя и фильтра
        if user.role in ['admin', 'moderator']:
            analyses = Analyse.objects.all()
        else:
            analyses = Analyse.objects.filter(user_key=user)
        
        # фильтр по статусу удаления
        if show_filter == 'active':
            analyses = analyses.filter(is_deleted=False)
        elif show_filter == 'deleted':
            analyses = analyses.filter(is_deleted=True)
        # all - без фильтра по статусу
        
        count = analyses.count()
        
        if count == 0:
            return JsonResponse({
                "success": False, 
                "message": "Нет записей для удаления."
            }, status=400)
        
        # проверка прав на полное удаление
        if permanent and user.role == 'regular':
            return JsonResponse({
                "success": False, 
                "message": "Обычные пользователи не могут удалять записи навсегда."
            }, status=403)
        
        # удаление записей
        deleted_count = 0
        if permanent:
            # полное удаление
            for analyse in analyses:
                try:
                    # удаляем файл изображения
                    if os.path.exists('python_picture_web' + str(analyse.image.url)):
                        os.remove('python_picture_web' + str(analyse.image.url))
                    analyse.delete()
                    deleted_count += 1
                except Exception as e:
                    print(f"Ошибка при удалении записи {analyse.id}: {str(e)}")
            
            message = f"Удалено навсегда: {deleted_count} записей"
        else:
            # мягкое удаление (только для активных записей)
            if show_filter == 'deleted':
                return JsonResponse({
                    "success": False,
                    "message": "Для уже удаленных записей невозможно мягкое удаление."
                }, status=400)
            
            # мягко удаляются только активные записи
            active_analyses = analyses.filter(is_deleted=False)
            deleted_count = active_analyses.count()
            active_analyses.update(is_deleted=True)
            
            message = f"Помечено как удалено: {deleted_count} записей"
        
        return JsonResponse({
            "success": True,
            "message": message,
            "count": deleted_count,
            "permanent": permanent,
            "show_filter": show_filter
        })

    return JsonResponse({"success": False, "message": "Метод не поддерживается."}, status=405)

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def classification_image(request: Request, key):
    method_name = "classification_image"
    try:
        image = request.FILES['image']
        image_data = image.read()
        result = MainImageClassifierBySkinLesion().apply(image_data)

        individual_labels = [label for label, _ in result['individual_predictions']]
        individual_probability = [max(probability) for _, probability in result['individual_predictions']]
        ensemble_label = result['ensemble_prediction'][0]

        model_1 = individual_labels[0]
        model_2 = individual_labels[1]
        model_3 = individual_labels[2]
        ensemble = ensemble_label

        model_1_probability =individual_probability[0]
        model_2_probability =individual_probability[1]
        model_3_probability =individual_probability[2]
        ensemble_probability = max(result['ensemble_prediction'][1])

        data = {
            "model_1": model_1,
            "model_2": model_2,
            "model_3": model_3,
            "ensemble": ensemble,
            "model_1_probability": model_1_probability,
            "model_2_probability": model_2_probability,
            "model_3_probability": model_3_probability,
            "ensemble_probability": ensemble_probability,
            "patient": request.POST.get('patient'),
            "description": request.POST.get('description')
        }

        files = {"image": (image.name, image_data, image.content_type)}
        response = requests.post(f'http://back:8000/cnn_table/{key}/add', data=data, files=files)
        return Response(response)
    except Exception as exc:
        response_status = status.HTTP_400_BAD_REQUEST
        exception = exc
        return Response({'error': str(exception)}, status=response_status)

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def classification_images(request: Request, key):
    method_name = "classification_images"
    try:
        images = request.FILES.getlist('images')
        for image in images:
            image_data = image.read()
            result = MainImageClassifierBySkinLesion().apply(image_data)

            individual_labels = [label for label, _ in result['individual_predictions']]
            individual_probability = [max(probability) for _, probability in result['individual_predictions']]
            ensemble_label = result['ensemble_prediction'][0]

            model_1 = individual_labels[0]
            model_2 = individual_labels[1]
            model_3 = individual_labels[2]
            ensemble = ensemble_label

            model_1_probability = individual_probability[0]
            model_2_probability = individual_probability[1]
            model_3_probability = individual_probability[2]
            ensemble_probability = max(result['ensemble_prediction'][1])

            model_1_probability =individual_probability[0]
            model_2_probability =individual_probability[1]
            model_3_probability =individual_probability[2]
            ensemble_probability = max(result['ensemble_prediction'][1])

            data = {
                "model_1": model_1,
                "model_2": model_2,
                "model_3": model_3,
                "ensemble": ensemble,
                "model_1_probability": model_1_probability,
                "model_2_probability": model_2_probability,
                "model_3_probability": model_3_probability,
                "ensemble_probability": ensemble_probability,
                "patient": request.POST.get('patient'),
                "description": request.POST.get('description')
            }

            files = {"image": (image.name, image_data, image.content_type)}
            responses = []
            responses.append(requests.post(f'http://back:8000/cnn_table/{key}/add', data=data, files=files))
        return Response({"responses": responses}, status=status.HTTP_200_OK)
    except Exception as exc:
        response_status = status.HTTP_400_BAD_REQUEST
        exception = exc
        return Response({'error': str(exception)}, status=response_status)

@csrf_exempt
def update_analyse(request, key):
    if request.method == 'POST':
        try:
            user = Users.objects.get(key=key)
        except Users.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Пользователь не найден.'}, status=404)

        try:
            data = json.loads(request.body.decode('utf-8'))
            record_id = data.get('id')
            description = data.get('description')
            diagnosis = data.get('diagnosis')

            if not all([record_id, description, diagnosis]):
                return JsonResponse({'success': False, 'message': 'Не все обязательные поля заполнены.'}, status=400)

            analyse = Analyse.objects.get(id=record_id, user_key=user)
            analyse.description = description
            analyse.diagnosis = diagnosis
            analyse.save()

            return JsonResponse({'success': True, 'message': 'Запись успешно обновлена.'})
        except Analyse.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Запись не найдена.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ошибка: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Метод не поддерживается.'}, status=405)
