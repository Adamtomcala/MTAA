from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login),
    path('login1/', views.login1),
    path('message/', views.message),
    path('user/', views.password),
    path('name/<str:username>', views.find_user),
    path('materials/<str:user_id>', views.upload_file),
    path('delete_material/<str:material_name>/<int:user_id>', views.delete_file),
    path('material', views.materials),
    path('return_material', views.return_material),
    path('return_classroom_materials/', views.return_classroom_materials),
    path('register', views.registration),
    path('add_user/<str:classroom_name>/<str:user_name>/<str:teacher_name>/', views.add_student_to_classroom),
    path('users/<str:classroom_name>', views.return_classroom_users),
    path('create_classroom/', views.create_classroom),
    path('return_all_classrooms/', views.return_all_classrooms),

]