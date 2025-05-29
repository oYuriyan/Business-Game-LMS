from django.db import models
from .partida import Partida
from .produtos import Produto
from django.contrib.auth.models import User
from django.utils import timezone

class Rodada(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    numero = models.PositiveIntegerField()
    ativo = models.BooleanField(default=False)
    data_inicio = models.DateTimeField(default=timezone.now)
    data_fim = models.DateTimeField(null=True, blank=True)

    produto_demandado = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True, blank=True, related_name='rodadas_demandadas')
    quantidade_demandada = models.PositiveIntegerField(null=True, blank=True)
    
    destino_demanda = models.CharField(max_length=100, null=True, blank=True)
    preco_maximo_aceitavel = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Opcional: se o "comprador" tem um teto

    decisao_jogadores = models.JSONField(default=dict)
    resultados = models.JSONField(default=dict)  # Armazenará o resultado da rodada (ranking, custos, etc.)
    
    decisao_jogadores = models.JSONField(default=dict)
    resultados = models.JSONField(default=dict)  # Armazenará o resultado da rodada (ranking, custos, etc.)

    class Meta:
        ordering = ['numero']

    def __str__(self):
        return f"Rodada {self.numero} - {self.partida.nome}"
