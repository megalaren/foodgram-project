from django.conf import settings
from django.conf.urls import handler404, handler500  # noqa
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

handler404 = 'recipes.views.page_not_found'  # noqa
handler500 = 'recipes.views.server_error'  # noqa

urlpatterns = [
    path('about/', include('about.urls', namespace='about')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('recipes.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
