import random
from .models import Users

from django.shortcuts import HttpResponse

# Create your views here.


def authorization(request):
    if request.GET:
        users = Users.objects.all()
        for _user in users:
            if _user.login == "admin" and _user.password == "1234":
                a = random.randint(1000, 9999)
                _user.key = a
                _user.authorization = True
                _user.save(update_fields=["key", "authorization"])
                return HttpResponse(_user.key)
            else:
                return HttpResponse("User not found.")


