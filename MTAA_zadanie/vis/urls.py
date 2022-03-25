from django.urls import path

from . import views

urlpatterns = [
    path('login/<str:username>/<str:password>', views.login),
    path('message', views.message),
    path('user/<str:username>/<str:password>', views.password),
    path('name/<str:username>', views.find_user),
    path('materials/<str:user_id>', views.upload_file),
]