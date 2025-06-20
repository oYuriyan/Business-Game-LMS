from django.db import models
from .partida import JogadorPartida
from .produtos import Produto

class Unidade(models.Model):
    """ Representa uma unidade de estoque (CD ou Fábrica) de um jogador. """
    jogador_partida = models.ForeignKey(JogadorPartida, on_delete=models.CASCADE, related_name='unidades')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    localidade = models.CharField(max_length=100, help_text="Nome da Unidade/CD, ex: Unidade 1, CD São Paulo")
    quantidade = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('jogador_partida', 'produto', 'localidade')
        verbose_name = "Unidade de Estoque"
        verbose_name_plural = "Unidades de Estoque"

    def __str__(self):
        return f"Estoque de {self.produto.nome} em {self.localidade} para {self.jogador_partida.jogador.username}"
