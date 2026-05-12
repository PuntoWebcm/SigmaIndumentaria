import mercadopago
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings  # Importamos los settings para usar las llaves de Render
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart

# --- CONFIGURACIÓN DE DOMINIO ---
# En Render, Django usa esto para saber a dónde volver tras el pago
DOMAIN = "https://sigmaindumentaria.onrender.com" 

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            # Guardamos el ID en la sesión para el siguiente paso
            request.session['order_id'] = order.id
            return redirect('orders:payment_selection')
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})

def payment_selection(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    # Inicializar SDK usando el Token que configuramos en las variables de entorno de Render
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    # Configuración de la preferencia
    preference_data = {
        "items": [
            {
                "title": f"Compra en SIGMA - Pedido #{order.id}",
                "quantity": 1,
                "unit_price": float(order.get_total_cost()),
                "currency_id": "ARS",
            }
        ],
        "back_urls": {
            "success": f"{DOMAIN}/orders/success/",
            "failure": f"{DOMAIN}/orders/payment/",
            "pending": f"{DOMAIN}/orders/success/"
        },
        "auto_return": "approved",
        "binary_mode": True,
    }

    # Crear la preferencia en MP
    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    
    # Log para ver en consola de Render si hay errores
    if "id" not in preference:
        print("ERROR MP:", preference)
    
    preference_id = preference.get('id', '')

    # PASAMOS LA PUBLIC_KEY AL HTML PARA QUE EL BOTÓN NO SEA GRIS
    return render(request, 'orders/order/payment.html', {
        'order': order,
        'preference_id': preference_id,
        'public_key': settings.MERCADOPAGO_PUBLIC_KEY  # <--- ESTO ARREGLA EL BOTÓN
    })

def payment_success(request):
    payment_id = request.GET.get('collection_id') or request.GET.get('payment_id')
    
    # Obtenemos el ID del pedido que guardamos en la sesión antes de pagar
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    # Vaciamos el carrito
    cart = Cart(request)
    cart.clear()
    
    return render(request, 'orders/order/created.html', {
        'payment_id': payment_id,
        'order': order,  # <--- Pasamos el pedido completo al HTML
    })