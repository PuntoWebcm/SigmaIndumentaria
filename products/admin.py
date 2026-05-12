from django.contrib import admin
from .models import Category, Product, Size

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']
    # Esto es opcional, pero ayuda si querés ordenar los talles alfabéticamente
    ordering = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Agregué 'category' al listado para que sepas de qué sección es cada cosa
    list_display = ['name', 'category', 'price', 'stock', 'available', 'created']
    list_filter = ['available', 'category', 'created']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    
    # Esto permite elegir los talles usando un buscador horizontal más cómodo 
    # en lugar de una lista simple hacia abajo
    filter_horizontal = ['sizes']