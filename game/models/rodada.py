from django.db import models
from .partida import Partida
from django.contrib.auth.models import User
from django.utils import timezone

class Rodada(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    numero_rodada = models.PositiveIntegerField()
    ativo = models.BooleanField(default=False)
    data_inicio = models.DateTimeField(default=timezone.now)
    data_fim = models.DateTimeField(default=timezone.now)
    
    decisao_jogadores = models.JSONField(default=dict)  # Pode armazenar as decisões em formato JSON
    resultados = models.JSONField(default=dict)  # Armazenará o resultado da rodada (ranking, custos, etc.)

    class Meta:
        ordering = ['numero_rodada']

    def __str__(self):
        return f"Rodada {self.numero_rodada} - {self.partida.nome}"
