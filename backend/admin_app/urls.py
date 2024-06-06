from django.urls import path
from . import views

urlpatterns = [
    path('dashboard_data/', views.dashboard_data, name='dashboard_data'),
    path('doughnut_chart_data/', views.doughnut_chart_data, name='doughnut_chart_data'),
    path('bar_chart_data/', views.bar_chart_data, name='bar_chart_data'),
    path('expensive_items_data/', views.expensive_items_data, name='expensive_items_data'),
    path('cheap_items_data/', views.cheap_items_data, name='cheap_items_data'),
    path('price_distribution_data/', views.price_distribution_data, name='price_distribution_data'),
]