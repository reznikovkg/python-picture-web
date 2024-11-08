import random
from .models import Users

from django.shortcuts import HttpResponse

# Create your views here.


def authorization(request):
    if request.GET: 
        users = Users.objects.all()
        login = request.GET.get("login")
        password = request.GET.get("password")
        for _user in   users:
            if _user.login == login and _user.password == password:
                a = random.randint(1000, 9999)
                _user.key = a
                _user.authorization = True
                _user.save(update_fields=["key", "authorization"])
                return HttpResponse(_user.key)
            elif _user.password != password:
                return HttpResponse("Incorrect password.", status=404)
            else:
                return HttpResponse("User not found.", status=404)


