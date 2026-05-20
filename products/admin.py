from django.contrib import admin
from .models import Category, Product, Size, ProductImage, Color  # <-- Importamos Color

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']
    ordering = ['name']

# --- NUEVO: REGISTRAMOS EL MODELO COLOR PARA QUE APAREZCA EN EL MENÚ IZQUIERDO ---
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name']
    ordering = ['name']  # Ordena los colores alfabéticamente en la lista

# --- ESTA CLASE PERMITE CARGAR LAS IMÁGENES EXTRAS EN LA MISMA PANTALLA ---
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  
    verbose_name = "Imagen adicional"
    verbose_name_plural = "Imágenes adicionales"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'available', 'created']
    list_filter = ['available', 'category', 'created']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    
    # AGREGAMOS 'colors' AQUÍ ABAJO:
    # Esto transforma la lista blanca incómoda en el selector horizontal con buscador doble
    filter_horizontal = ['sizes', 'colors']
    
    inlines = [ProductImageInline]