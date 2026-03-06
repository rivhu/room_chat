from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('room/create/', views.create_room_view, name='create_room'),
    path('room/<str:room_name>/', views.room_view, name='room'),
    path('room/<str:room_name>/delete/', views.delete_room_view, name='delete_room'),
    path('private/<str:username>/', views.private_chat_view, name='private_chat'),
]
