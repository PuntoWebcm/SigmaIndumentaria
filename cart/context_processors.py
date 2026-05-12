from .cart import Cart

def cart(request):
    # Esto solo debe retornar el objeto Cart, no hacer cálculos matemáticos
    # que se guarden en la sesión.
    return {'cart': Cart(request)}