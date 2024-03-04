from django.urls import path
from .views import add_to_shopping_list, get_shopping_list_items, update_list_items, delete_list_item
from django.conf import settings
from django.conf.urls.static import static
# from django.views.decorators.csrf import get_token

urlpatterns = [
    path('shopping_list/', add_to_shopping_list, name='add_to_shopping_list'),
    path('get_list_items/', get_shopping_list_items, name='get_shopping_list_items'),
    path('update_list_items/', update_list_items, name='update_list_items'),
    path('delete_list_item/', delete_list_item, name='delete_list_item'),

]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
