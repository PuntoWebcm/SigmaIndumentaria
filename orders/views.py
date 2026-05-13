import mercadopago
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from urllib.parse import quote

# --- CONFIGURACIÓN DE DOMINIO ---
DOMAIN = "https://sigmaindumentaria.onrender.com" 

def order_create(request):
    cart = Cart(request)
    
    # --- VALIDACIÓN MÍNIMO DE COMPRA $50.000 ---
    if cart.get_total_price() < 50000:
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Usamos commit=False para poder agregar el envío antes de guardar
            order = form.save(commit=False)
            
            # --- RECUPERAR COSTO DE ENVÍO DE LA SESIÓN ---
            # Si el cliente usó el calculador, el dato estará acá. 
            # Si no, por defecto es 0.
            shipping_cost = request.session.get('shipping_cost', 0)
            order.shipping_cost = shipping_cost
            
            order.save() # Ahora sí guardamos en la DB
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                    size=item['size']
                )
            
            # Limpiamos el envío de la sesión una vez usado
            if 'shipping_cost' in request.session:
                del request.session['shipping_cost']
                
            request.session['order_id'] = order.id
            return redirect('orders:payment_selection')
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})

def payment_selection(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    # Mercado Pago ahora toma el costo TOTAL (Productos + Envío)
    # gracias al cambio que hicimos en el método get_total_cost del modelo.
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

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    
    if "id" not in preference:
        print("ERROR MP:", preference)
    
    preference_id = preference.get('id', '')

    return render(request, 'orders/order/payment.html', {
        'order': order,
        'preference_id': preference_id,
        'public_key': settings.MERCADOPAGO_PUBLIC_KEY 
    })

def payment_success(request):
    payment_id = request.GET.get('collection_id') or request.GET.get('payment_id')
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    # Marcar como pagado
    order.paid = True
    order.save()
    
    items = order.items.all() 
    detalle_productos = ""
    
    for item in items:
        detalle_productos += f"- {item.quantity}x {item.product.name} (Talle: {item.size})\n"
        # Descuento de stock
        producto = item.product
        producto.stock = max(0, producto.stock - item.quantity)
        producto.save()

    # --- ENVÍO DE WHATSAPP CON DATOS COMPLETOS ---
    try:
        mi_numero = "5493584304880"
        mi_apikey = "2153232"
        
        mensaje_texto = (
            f"🚀 *NUEVA VENTA SIGMA*\n\n"
            f"📦 *Pedido:* #{order.id}\n"
            f"👤 *Cliente:* {order.first_name} {order.last_name}\n"
            f"📱 *WhatsApp:* {order.phone}\n"
            f"📍 *Dirección:* {order.address}\n"
            f"🌆 *Ciudad:* {order.city} ({order.postal_code})\n\n"
            f"🛒 *Productos:*\n{detalle_productos}\n"
            f"🚚 *Envío cobrado:* ${order.shipping_cost}\n" # <-- AHORA SE INCLUYE
            f"💰 *Total Cobrado:* ${float(order.get_total_cost())}\n"
            f"💳 *Pago ID:* {payment_id}"
        )

        mensaje_url = quote(mensaje_texto)
        url_bot = f"https://api.callmebot.com/whatsapp.php?phone={mi_numero}&text={mensaje_url}&apikey={mi_apikey}"
        
        response = requests.get(url_bot, timeout=10)
        
        if response.status_code == 200:
            print("WhatsApp enviado con éxito")
        else:
            print(f"Error en CallMeBot: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error enviando WhatsApp: {e}")
    
    cart = Cart(request)
    cart.clear()
    
    return render(request, 'orders/order/created.html', {
        'payment_id': payment_id,
        'order': order
    })