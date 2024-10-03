from django.shortcuts import HttpResponse
from users.models import Users
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