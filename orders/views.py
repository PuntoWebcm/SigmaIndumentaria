import mercadopago
from django.shortcuts import render, redirect, get_object_or_404
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart

# --- CONFIGURACIÓN DE DOMINIO ---
# Cuando estés en Render, cambiá esto por "https://tu-app.onrender.com"
DOMAIN = "http://127.0.0.1:8000" 

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
    
    # Inicializar SDK de Mercado Pago
    sdk = mercadopago.SDK("APP_USR-5094495747115735-051213-2a0002dd344fe48127fc3b416ddaab5f-3396045717")

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
        "binary_mode": True, # Evita el estado "en proceso" para tarjetas
    }

    # Crear la preferencia en MP
    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    
    # Log para ver en consola si hay errores de MP
    if "id" not in preference:
        print("ERROR MP:", preference)
    
    preference_id = preference.get('id', '')

    return render(request, 'orders/order/payment.html', {
        'order': order,
        'preference_id': preference_id
    })

def payment_success(request):
    # MP envía collection_id o payment_id por la URL al retornar
    payment_id = request.GET.get('collection_id') or request.GET.get('payment_id')
    
    # Vaciamos el carrito recién aquí, tras confirmar el retorno
    cart = Cart(request)
    cart.clear()
    
    return render(request, 'orders/order/created.html', {
        'payment_id': payment_id
    })