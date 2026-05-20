from decimal import Decimal
from django.conf import settings
from products.models import Product

class Cart:
    def __init__(self, request):
        """
        Inicializa el carrito usando la sesión de Django.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Si no hay carrito, creamos uno vacío en la sesión
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False, size=None):
        """
        Añade un producto al carrito o actualiza su cantidad.
        """
        product_id = str(product.id)
        size_str = str(size) if size and size != "Único" else "Unico"
        # Creamos una llave única que combine ID y Talle
        item_key = f"{product_id}_{size_str}"

        if item_key not in self.cart:
            self.cart[item_key] = {
                'quantity': 0,
                'price': str(product.price), # Guardamos como string para evitar error JSON
                'size': size_str
            }
        
        if override_quantity:
            self.cart[item_key]['quantity'] = quantity
        else:
            self.cart[item_key]['quantity'] += quantity
        
        self.save()

    def save(self):
        # Marcar la sesión como modificada para que Django la guarde
        self.session.modified = True

    def remove(self, product_id, size=None):
        """
        Elimina un producto del carrito.
        """
        product_id = str(product_id)
        size_str = str(size) if size and size != "Único" else "Unico"
        item_key = f"{product_id}_{size_str}"
        
        if item_key in self.cart:
            del self.cart[item_key]
        self.save()

    def __iter__(self):
        product_ids = [key.split('_')[0] for key in self.cart.keys()]
        products = Product.objects.filter(id__in=product_ids)
        
        # Hacemos una copia profunda para no ensuciar self.cart con objetos Decimal
        import copy
        current_cart = copy.deepcopy(self.cart)

        for product in products:
            for key in current_cart:
                if key.startswith(f"{product.id}_"):
                    current_cart[key]['product'] = product

        for item in current_cart.values():
            # Convertimos a Decimal solo en la copia que va al HTML
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            
            size_value = item.get('size', 'Unico')
            item['size_display'] = "Único" if size_value == "Unico" else size_value
            
            yield item

    def __len__(self):
        """
        Cuenta el total de unidades en el carrito.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Calcula el costo total del carrito regresando un Decimal para el template,
        pero sin modificar el diccionario que se guarda en la sesión.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Vacía el carrito de la sesión.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()

    # --- NUEVOS MÉTODOS PARA EL MÍNIMO DE COMPRA ---

    def get_min_purchase_amount(self):
        """Monto mínimo de compra requerido ($30.000)."""
        return Decimal('30000')

    def is_min_purchase_valid(self):
        """Devuelve True si el carrito alcanza o supera los $30.000."""
        return self.get_total_price() >= self.get_min_purchase_amount()

    def get_remaining_for_min(self):
        """Devuelve cuánto dinero falta para alcanzar el mínimo."""
        remaining = self.get_min_purchase_amount() - self.get_total_price()
        return max(Decimal('0'), remaining)