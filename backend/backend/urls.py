from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
# from django.views.decorators.csrf import get_token

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include('authentication_app.urls')),
    path('api/', include('raw_food_item.urls')),
    path('api/', include('raw_food_price.urls')),
    path('api/', include('shopping_list.urls')),
    path('contact/', include('feedback.urls')),
    path('newsletter/', include('newsletter.urls')),
    # path('api/', include('admin_app.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    # path('csrf/', get_token, name='csrf'),

    # path('', include('frontend.urls'))
]

urlpatterns += [re_path(r'^.*', TemplateView.as_view(template_name='index.html'))]
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)