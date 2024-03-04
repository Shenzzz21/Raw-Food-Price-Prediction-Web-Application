from django.urls import path
from .views import add_item, get_items, prediction_page_items, get_item_data, get_items_by_category, get_categories, search_items, update_item
from django.conf import settings
from django.conf.urls.static import static
# from django.views.decorators.csrf import get_token

urlpatterns = [
    path('add_item/', add_item, name='add_item'),
    path('get_items/', get_items, name='get_items'),
    path('prediction_page_items/', prediction_page_items, name='prediction_page_items'),
    path('item/<int:item_id>/', get_item_data, name='get_item_data'),
    # path('get_items_compare/', get_items_compare, name='get_items_compare'),
    # path('get_item_details/<int:item_id>/', get_item_details, name='get_item_details'),
    path('get_items_by_category/', get_items_by_category, name='get_items_by_category'),
    path('get_categories/', get_categories, name='get_categories'),
    path('search_items/', search_items, name='search_items'),
    path('update_item/', update_item, name='update_item'),
    # Endpoint to fetch CSRF token
    # path('
    # csrf/', csrf_token, name='csrf_token'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
