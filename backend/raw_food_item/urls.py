from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('update_predictions/', views.update_predictions, name='update_predictions'),
    path('predict_price/', views.predict_price, name='predict_price'),
    path('add_item/', views.add_item, name='add_item'),
    path('get_items/', views.get_items, name='get_items'),
    path('prediction_page_items/', views.prediction_page_items, name='prediction_page_items'),
    path('item/<int:item_id>/', views.get_item_data, name='get_item_data'),
    path('get_items_by_category/', views.get_items_by_category, name='get_items_by_category'),
    path('item/<int:item_id>/time_series/', views.get_data_time_series, name='get_item_time_series_data'),
    path('search_items/', views.search_items, name='search_items'),
    path('update_item/', views.update_item, name='update_item'),
    path('delete_item/', views.delete_item, name='delete_item'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)