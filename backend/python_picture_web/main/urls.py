from django.urls import path
from . import views

urlpatterns = [
    path('download/', views.download_picture),
    path('generate/', views.cnn_response_generate),
]