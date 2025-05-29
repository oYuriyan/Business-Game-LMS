from django.db import models
from .partida import JogadorPartida
from .produtos import Produto

class EstoqueJogador(models.Model):
    jogador_partida = models.ForeignKey(JogadorPartida, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('jogador_partida', 'produto') # Garante um estoque por produto para cada jogador na partida

    def __str__(self):
        return f"Estoque de {self.produto.nome} para {self.jogador_partida.jogador.username} na partida {self.jogador_partida.partida.nome}: {self.quantidade}"