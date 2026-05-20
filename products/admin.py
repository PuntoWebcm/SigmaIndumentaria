from django.contrib import admin
from .models import Category, Product, Size, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']
    # Esto es opcional, pero ayuda si querés ordenar los talles alfabéticamente
    ordering = ['name']

# --- ESTA CLASE PERMITE CARGAR LAS IMÁGENES EXTRAS EN LA MISMA PANTALLA ---
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # Te va a mostrar 3 casilleros vacíos listos para meter fotos extras juntas
    verbose_name = "Imagen adicional"
    verbose_name_plural = "Imágenes adicionales"

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
    
    # ASOCIAMOS LA GALERÍA PARA QUE APAREZCA ABAJO DEL PRODUCTO
    inlines = [ProductImageInline]