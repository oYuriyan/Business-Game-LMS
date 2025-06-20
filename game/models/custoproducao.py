from django.db import models
from .produtos import Produto
from decimal import Decimal

class CustoProducao(models.Model):
    """
    Armazena o custo de produção de um Produto para uma Empresa Modelo específica.
    Ex: Custo da Cafeteira para a "Empresa A" é R$ 30,00.
    """
    nome_empresa_template = models.CharField(max_length=50, help_text="Ex: Empresa A, Empresa B...")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        # Garante que só existe um custo por empresa/produto
        unique_together = ('nome_empresa_template', 'produto')
        verbose_name = "Custo de Produção"
        verbose_name_plural = "Custos de Produção"

    def __str__(self):
        return f"Custo de {self.produto.nome} para {self.nome_empresa_template}: R$ {self.custo_unitario}"