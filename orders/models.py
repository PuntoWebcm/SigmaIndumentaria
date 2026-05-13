from django.db import models
from products.models import Product

class Order(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="Nombre")
    last_name = models.CharField(max_length=50, verbose_name="Apellido")
    email = models.EmailField()
    phone = models.CharField(max_length=20, verbose_name="Teléfono / WhatsApp")
    address = models.CharField(max_length=250, verbose_name="Dirección")
    postal_code = models.CharField(max_length=20, verbose_name="Código Postal")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    
    # Campo nuevo para el costo de envío
    shipping_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name="Costo de Envío"
    )
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False, verbose_name="Pagado")

    class Meta:
        ordering = ['-created']
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f'Pedido {self.id}'

    # Modificado para sumar productos + envío
    def get_total_cost(self):
        total_items = sum(item.get_cost() for item in self.items.all())
        return total_items + self.shipping_cost

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=20, default="Unico")

    def __str__(self):
        return f'ID Item: {self.id}'

    def get_cost(self):
        return self.price * self.quantity