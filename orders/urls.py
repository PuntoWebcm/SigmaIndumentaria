from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('payment/', views.payment_selection, name='payment_selection'),
    # AGREGAMOS ESTA LÍNEA:
    path('success/', views.payment_success, name='payment_success'),
]