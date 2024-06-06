from django.urls import path
from . import views

urlpatterns = [
    path('get_categories/', views.get_categories, name='get_categories'),
    path('add_category/', views.add_category, name='add_category'),
    path('search_categories/', views.search_categories, name='search_categories'),
    path('update_category/', views.update_category, name='update_category'),
    path('delete_category/', views.delete_category, name='delete_category'),
    path('filter_items/', views.filter_items_by_category, name='filter_items_by_category'),
]