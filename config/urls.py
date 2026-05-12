from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')), # <--- NUEVA LÍNEA
    path('', include('products.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Configuración del Panel de Control (fuera del if para que siempre funcione)
admin.site.site_header = "Panel de Control Sigma Indumentaria"
admin.site.site_title = "Sigma Admin"
admin.site.index_title = "Gestión de la Tienda"