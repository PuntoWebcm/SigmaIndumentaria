from django import forms
from products.models import Size, Color  # <-- Importamos el nuevo modelo Color

class CartAddProductForm(forms.Form):
    # La cantidad la ocultamos (HiddenInput) para que por defecto sea 1
    quantity = forms.IntegerField(initial=1, widget=forms.HiddenInput)
    
    # El selector de talles
    size = forms.ModelChoiceField(
        queryset=Size.objects.none(), # Empezamos vacío
        empty_label="Seleccioná tu talle",
        label="Talle",
        widget=forms.Select(attrs={'class': 'form-select mb-3'})
    )

    # NUEVO: El selector de colores
    color = forms.ModelChoiceField(
        queryset=Color.objects.none(), # Empezamos vacío y se llena dinámicamente
        empty_label="Seleccioná tu color",
        label="Color",
        widget=forms.Select(attrs={'class': 'form-select mb-3'})
    )

    def __init__(self, *args, **kwargs):
        # Recibimos el producto para saber qué talles y colores mostrar
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        if product:
            self.fields['size'].queryset = product.sizes.all()
            # LLENAMOS LOS COLORES DISPONIBLES DE ESTE PRODUCTO:
            self.fields['color'].queryset = product.colors.all()