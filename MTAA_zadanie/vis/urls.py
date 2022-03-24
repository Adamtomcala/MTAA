from django.urls import path

from . import views

urlpatterns = [
    path('login/<str:username>/<str:password>', views.login),
    path('messages', views.get_messages),
    path('user/<str:username>/<str:password>', views.password),
    path('name/<str:username>', views.find_user),
]