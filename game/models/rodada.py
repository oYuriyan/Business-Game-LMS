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

    produto_demandado = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True, blank=True)
    quantidade_demandada = models.PositiveIntegerField(null=True, blank=True)
    destino_demanda = models.CharField(max_length=100, null=True, blank=True)
    
    resultados = models.JSONField(default=dict, blank=True)
    class Meta:
        ordering = ['numero']
        unique_together = ('partida', 'numero')

    def __str__(self):
        return f"Rodada {self.numero} - {self.partida.nome}"
