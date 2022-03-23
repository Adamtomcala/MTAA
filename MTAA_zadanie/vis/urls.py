from django.urls import path

from . import views

urlpatterns = [
    path('login/<str:username>/<str:password>', views.login),
    path('messages', views.get_messages)
]