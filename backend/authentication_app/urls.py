from django.urls import path
from . import views

urlpatterns = [
    path('get_users/', views.get_users, name='get_users'),
    path('check_is_admin/', views.check_is_admin, name='check_is_admin'),
    path('search_users/', views.search_users, name='search_users'),
    path('update_user/', views.update_user, name='update_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('user_details/', views.user_details, name='user_details'),
    path('update_profile/', views.update_profile, name='update_profile'),
]