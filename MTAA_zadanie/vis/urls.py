from django.urls import path

from . import views

urlpatterns = [
    path('login/<str:username>/<str:password>', views.login),
    path('message', views.message),
    path('user/<str:username>/<str:password>', views.password),
    path('name/<str:username>', views.find_user),
    path('materials/<str:user_id>', views.upload_file),
    path('delete_material/<int:material_id>', views.delete_file),
    path('material', views.materials),
    path('register', views.registration),
    path('add_user/<str:classroom_name>/<str:user_name>/<str:teacher_name>', views.add_student_to_classroom),
    path('users/<str:classroom_name>', views.return_classroom_users),
]