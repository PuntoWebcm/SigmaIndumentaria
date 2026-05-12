from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages  # Para los Toasts de éxito
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
    size = request.GET.get('size')
    
    cart.remove(product_id, size=size)
    messages.info(request, "Producto eliminado del carrito.")
    
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    # IMPORTANTE: No debe haber cart.clear() aquí para que no se vacíe solo
    return render(request, 'cart/detail.html', {'cart': cart})