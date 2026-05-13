import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from products.models import Product
from .cart import Cart
from .forms import CartAddProductForm

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # Pasamos los datos del POST al formulario
    form = CartAddProductForm(request.POST, product=product)
    
    if form.is_valid():
        cd = form.cleaned_data
        
        # Lógica de talles
        if cd.get('size'):
            talle_nombre = str(cd['size'].name)
        else:
            talle_nombre = "Unico"
            
        cart.add(product=product, 
                 quantity=cd['quantity'], 
                 size=talle_nombre)
        
        messages.success(request, f'¡{product.name} se añadió al carrito!')
    else:
        # Fallback por si hay error en el formulario
        cart.add(product=product, quantity=1, size="Unico")
        messages.success(request, f'¡{product.name} añadido!')
    
    # Redirigimos al catálogo para que el usuario vea el Toast y siga comprando
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

def cart_remove(request, product_id):
    cart = Cart(request)
    # Cambiamos a POST si el formulario de borrado usa POST, 
    # o mantenemos GET según cómo esté tu template.
    size = request.POST.get('size') or request.GET.get('size')
    
    cart.remove(product_id, size=size)
    messages.info(request, "Producto eliminado del carrito.")
    
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})

# --- NUEVA FUNCIÓN PARA EL ENVÍO ---
def cart_add_shipping(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            costo = int(data.get('costo', 0))
            zona = data.get('zona', '')
            
            # Guardamos en la sesión para que orders/views.py lo pueda leer después
            request.session['shipping_cost'] = costo
            request.session['shipping_zona'] = zona
            
            return JsonResponse({'status': 'ok', 'costo': costo})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)