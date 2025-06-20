from django.db import models
from .produtos import Produto
from decimal import Decimal

class CustoTransporte(models.Model):
    nome_empresa_template = models.CharField(max_length=50, help_text="Ex: Empresa A")
    cd_origem = models.CharField(max_length=100, help_text="Ex: CD São Paulo")
    local_destino = models.CharField(max_length=100, help_text="Ex: Osasco")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    custo_unitario_transporte = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        unique_together = ('nome_empresa_template', 'cd_origem', 'local_destino', 'produto')
        verbose_name = "Custo de Transporte"
        verbose_name_plural = "Custos de Transporte"

    def __str__(self):
        return f"Frete de {self.produto.nome} ({self.nome_empresa_template}) de {self.cd_origem} para {self.local_destino}: R$ {self.custo_unitario_transporte}"