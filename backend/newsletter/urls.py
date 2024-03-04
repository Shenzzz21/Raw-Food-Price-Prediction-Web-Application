from django.urls import path
from .views import subscribe_newsletter, get_subscribers, send_newsletter, get_newsletters

urlpatterns = [
    # Other URL patterns
    path('subscribe_newsletter/', subscribe_newsletter, name='subscribe_newsletter'),
    path('get_subscribers/', get_subscribers, name='get_subscribers'),
    path('send_newsletter/', send_newsletter, name='send_newsletter'),
    path('get_newsletters/', get_newsletters, name='get_newsletters'),
]
