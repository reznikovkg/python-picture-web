import random
from .models import Users

from django.shortcuts import HttpResponse

# Create your views here.

def authorization(request, login, password):
    if request.GET:
        users = Users.objects.all()
        for _user in users:
            if _user.login == login and _user.password == password:
                a = random.randint(1000, 9999)
                _user.key = a
                _user.authorization = True
                _user.save(update_fields=["key", "authorization"])
                return HttpResponse(f"Key for login={login} and password={password} is {str(_user.key)}.")
            else:
                return HttpResponse("User not found.")


