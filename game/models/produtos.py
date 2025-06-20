from django.db import models
from decimal import Decimal

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    quantidade = models.PositiveIntegerField(default=0)
    categoria = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.nome