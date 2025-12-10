from django.urls import path
from . import views

urlpatterns = [
    path('auth', views.auth_view, name='auth'),
    # endpoints для управления пользователями
    path('users/<str:key>/list', views.users_list, name='users_list'),
    path('users/<str:key>/create', views.create_user, name='create_user'),
    path('users/<str:key>/update/<int:user_id>', views.update_user, name='update_user'),
    path('users/<str:key>/delete/<int:user_id>', views.delete_user, name='delete_user'),
    path('users/<str:key>/current', views.get_current_user, name='get_current_user'),
]
