from django.shortcuts import HttpResponse
from users.models import Users
import io

from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from image_classifier.main.run import MainImageClassifierBySkinLesion
# Create your views here.

def download_picture(request, login, key):
   if request.GET:
      users = Users.objects.all()
      for _user in users:
         if _user.login == login and _user.key == key:
            return HttpResponse("Picture is download")
         elif _user.login == login:
            return HttpResponse(f"Key={key} is incorrect.")
         else:
            return HttpResponse("User not found.")


def cnn_response_generate(request, login, key):
   if request.GET:
      users = Users.objects.all()
      for _user in users:
         if _user.login == login and _user.key == key:
            return HttpResponse("Model is generate")
         elif _user.login == login:
            return HttpResponse(f"Key={key} is incorrect.")
         else:
            return HttpResponse("User not found.")


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def classification_image(request: Request):
    method_name = "classification_image"
    try:
        image = request.FILES['image']
        image_data = image.read()
        result = MainImageClassifierBySkinLesion().apply(image_data)
        return Response(result)
    except Exception as exc:
        response_status = status.HTTP_400_BAD_REQUEST
        exception = exc
        return Response({'error': str(exception)}, status=response_status)
