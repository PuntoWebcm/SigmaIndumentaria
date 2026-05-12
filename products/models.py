from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='nombre')
    slug = models.SlugField(unique=True, verbose_name='enlace permanente')

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_list_by_category', args=[self.slug])


# --- NUEVO MODELO PARA TALLES ---
class Size(models.Model):
    name = models.CharField(max_length=10, verbose_name='talle')

    class Meta:
        verbose_name = 'talle'
        verbose_name_plural = 'talles'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products', 
        verbose_name='categoría'
    )
    name = models.CharField(max_length=200, verbose_name='nombre')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='enlace permanente')
    
    # Agregamos la relación con los talles
    sizes = models.ManyToManyField(
        Size, 
        related_name='products', 
        verbose_name='talles disponibles',
        blank=True
    )
    
    description = models.TextField(blank=True, verbose_name='descripción')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='precio')
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name='imagen')
    stock = models.IntegerField(default=0, verbose_name='stock total')
    available = models.BooleanField(default=True, verbose_name='disponible')
    created = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')
    updated = models.DateTimeField(auto_now=True, verbose_name='última actualización')

    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'
        ordering = ['-created']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])