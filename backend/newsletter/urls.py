from django.urls import path
from . import views

urlpatterns = [
    path('subscribe_newsletter/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('get_subscribers/', views.get_subscribers, name='get_subscribers'),
    path('send_newsletter/', views.send_newsletter, name='send_newsletter'),
    path('get_newsletters/', views.get_newsletters, name='get_newsletters'),
    path('unsubscribe/<str:uidb64>/<str:token>/', views.unsubscribe, name='unsubscribe'),
]