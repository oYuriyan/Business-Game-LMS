from django.db import models
from .partida import Partida

class Rodada(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    numero_rodada = models.PositiveIntegerField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"Rodada {self.numero_rodada} - {self.partida.nome}"