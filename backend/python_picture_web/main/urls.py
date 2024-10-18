from django.urls import path
from . import views

urlpatterns = [
    path('download/<str:login>/<int:key>/', views.download_picture),
    path('generate/<str:login>/<int:key>/', views.cnn_response_generate),
    path('classification-image', views.classification_image, name="classification_image")
]