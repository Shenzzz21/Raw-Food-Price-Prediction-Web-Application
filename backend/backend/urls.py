from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin URL
    path("admin/", admin.site.urls),

    # API URLs for django apps
    path('api/', include('authentication_app.urls')),
    path('api/', include('admin_app.urls')),
    path('api/', include('category.urls')),
    path('api/', include('raw_food_item.urls')),
    path('api/', include('raw_food_price.urls')),
    path('api/', include('shopping_list.urls')),
    path('contact/', include('feedback.urls')),
    path('newsletter/', include('newsletter.urls')),

    # Authentication URLs using Djoser
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]      + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Serve media files during development

# Catch-all URL pattern to serve index.html for client-side routing in single-page applications
urlpatterns += [re_path(r'^.*', TemplateView.as_view(template_name='index.html'))]