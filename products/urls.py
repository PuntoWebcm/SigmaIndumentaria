from django.urls import path
from . import views

urlpatterns = [
    # 1. Página principal (Muestra todo)
    path('', views.product_list, name='product_list'),
    
    # 2. Filtro por categoría (ej: /sweaters/)
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    
    # 3. Detalle del producto (ej: /product/sweater-rayado/)
    # Le agregamos 'item/' o 'product/' adelante para que no choque con la categoría
    path('item/<slug:slug>/', views.product_detail, name='product_detail'),
]