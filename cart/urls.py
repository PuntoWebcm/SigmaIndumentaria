from django.urls import path
from . import views

app_name = 'cart' # Esto es lo que registra el namespace

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    # Nueva ruta para procesar el envío por AJAX
    path('add-shipping/', views.cart_add_shipping, name='cart_add_shipping'),
]