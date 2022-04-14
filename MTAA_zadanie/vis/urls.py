from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login),
    path('login1/', views.login1),
    path('message/', views.message),
    path('user/', views.password),
    path('name/<str:username>', views.find_user),
    path('materials/<str:user_id>', views.upload_file),
    path('delete_material/<int:material_id>', views.delete_file),
    path('material', views.materials),
    path('register', views.registration),
    path('add_user/<str:classroom_name>/<str:user_name>/<str:teacher_name>', views.add_student_to_classroom),
    path('users/<str:classroom_name>', views.return_classroom_users),
]