from decimal import Decimal
from django.conf import settings
from products.models import Product, Color # <-- Importamos Color para poder mostrar su nombre real

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

    def add(self, product, quantity=1, override_quantity=False, size=None, color=None):
        """
        Añade un producto al carrito o actualiza su cantidad incluyendo Talle y Color.
        """
        product_id = str(product.id)
        
        # Procesamos el talle (igual que antes)
        size_str = str(size) if size and size != "Único" else "Unico"
        
        # NUEVO: Procesamos el color (Guardamos el ID para poder recuperarlo del formulario)
        color_str = str(color.id) if color and hasattr(color, 'id') else str(color) if color else "Unico"

        # Creamos una llave única hipersegura que combine ID, Talle y Color
        item_key = f"{product_id}_{size_str}_{color_str}"

        if item_key not in self.cart:
            self.cart[item_key] = {
                'quantity': 0,
                'price': str(product.price), # Guardamos como string para evitar error JSON
                'size': size_str,
                'color': color_str # NUEVO: Almacenamos el ID del color en la sesión
            }
        
        if override_quantity:
            self.cart[item_key]['quantity'] = quantity
        else:
            self.cart[item_key]['quantity'] += quantity
        
        self.save()

    def save(self):
        # Marcar la sesión como modificada para que Django la guarden en la DB
        self.session.modified = True

    def remove(self, product_id, size=None, color=None):
        """
        Elimina un producto del carrito considerando su talle y color exacto.
        """
        product_id = str(product_id)
        size_str = str(size) if size and size != "Único" else "Unico"
        color_str = str(color) if color else "Unico"
        
        # Armamos el item_key idéntico para borrar el producto correcto
        item_key = f"{product_id}_{size_str}_{color_str}"
        
        if item_key in self.cart:
            del self.cart[item_key]
        self.save()

    def __iter__(self):
        product_ids = [key.split('_')[0] for key in self.cart.keys()]
        products = Product.objects.filter(id__in=product_ids)
        
        # Buscamos todos los colores guardados en el carrito para traer sus nombres en una sola consulta limpia
        color_ids = [item.get('color') for item in self.cart.values() if item.get('color') != 'Unico']
        colors_dict = {str(c.id): c.name for c in Color.objects.filter(id__in=color_ids)}
        
        # Hacemos una copia profunda para no ensuciar self.cart con objetos Django/Decimal
        import copy
        current_cart = copy.deepcopy(self.cart)

        for product in products:
            for key in current_cart:
                if key.startswith(f"{product.id}_"):
                    current_cart[key]['product'] = product

        for key, item in current_cart.items():
            # Convertimos a Decimal solo en la copia que va al HTML
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            
            # Formateo de visualización de Talles
            size_value = item.get('size', 'Unico')
            item['size_display'] = "Único" if size_value == "Unico" else size_value
            
            # NUEVO: Formateo de visualización de Colores (Convierte el ID del color en su nombre real)
            color_value = item.get('color', 'Unico')
            if color_value == 'Unico':
                item['color_display'] = "Único"
            else:
                item['color_display'] = colors_dict.get(color_value, "No especificado")
            
            yield item

    def __len__(self):
        """
        Cuenta el total de unidades en el carrito.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Calcula el costo total del carrito regresando un Decimal para el template.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Vacía el carrito de la sesión.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()

    # --- MÉTODOS PARA EL MÍNIMO DE COMPRA ---

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