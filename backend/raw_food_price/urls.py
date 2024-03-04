from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    # Other URL patterns...
    path('add_item_price/', csrf_exempt(views.add_item_price), name='add_item_price'),
]
