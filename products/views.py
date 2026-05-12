from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from cart.forms import CartAddProductForm # Importamos el nuevo formulario

def product_list(request, category_slug=None):
    """
    Lista todos los productos o filtra por categoría.
    """
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'products/list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

def product_detail(request, slug):
    """
    Muestra el detalle del producto e incluye el formulario de talles.
    """
    product = get_object_or_404(Product, slug=slug, available=True)
    
    # Inicializamos el formulario de carrito pasando el producto 
    # para que solo muestre los talles que cargaste en el Admin
    cart_product_form = CartAddProductForm(product=product)
    
    return render(request, 'products/detail.html', {
        'product': product,
        'cart_product_form': cart_product_form
    })