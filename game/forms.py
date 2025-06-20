from django import forms
from .models import Produto

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'categoria', 'preco', 'quantidade']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'categoria': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'preco': forms.NumberInput(attrs={'class': 'mt-1 block w-full'}),
            'quantidade': forms.NumberInput(attrs={'class': 'mt-1 block w-full'}),
        }
