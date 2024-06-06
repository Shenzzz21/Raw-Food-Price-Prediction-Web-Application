from django.urls import path
from . import views

urlpatterns = [
    path('shopping_list/', views.add_to_shopping_list, name='add_to_shopping_list'),
    path('get_list_items/', views.get_shopping_list_items, name='get_shopping_list_items'),
    path('update_list_items/', views.update_list_items, name='update_list_items'),
    path('delete_list_item/', views.delete_list_item, name='delete_list_item'),
]