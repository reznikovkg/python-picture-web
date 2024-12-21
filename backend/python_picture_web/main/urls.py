from django.urls import path
from . import views

urlpatterns = [
    path('cnn_table/<str:key>/add', views.cnn_result_post),
    path('cnn_table/<str:key>/add_images', views.cnn_results_post),
    path('cnn_table/<str:key>/get', views.get_result),
    path('cnn_table/<str:key>/delete', views.delete_row),
    path('cnn_table/<str:key>/delete_all', views.delete_all),
    path('cnn_table/<str:key>/update', views.update_analyse, name='update_analyse'),
    path('classification-image/<str:key>', views.classification_image, name="classification_image"),
    path('classification-images/<str:key>', views.classification_images, name="classification_images"),
    path('cnn_table/<str:key>/add_recording', views.add_recording, name='add_recording')
]