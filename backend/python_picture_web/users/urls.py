from django.urls import path
from . import views

urlpatterns = [
    path('<str:login>/<str:password>/', views.authorization)
]