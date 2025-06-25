from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from .rodada import Rodada
from .partida import Partida
from .produtos import Produto
from .unidade import Unidade
from decimal import Decimal

class Decisao(models.Model):
    jogador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decisoes_jogador')
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name='decisoes_partida')
    rodada = models.ForeignKey(Rodada, on_delete=models.CASCADE, related_name='decisoes_rodada')
    unidade_origem = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name='decisoes_origem')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE) 
    quantidade_produzida = models.PositiveIntegerField(default=0)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    distribuicao = models.JSONField(default=dict) 
    
    custo_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    data_decisao = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('jogador', 'rodada', 'produto')

    def __str__(self):
        return f'{self.jogador.username} - {self.produto.nome} (Qtd: {self.quantidade_produzida}, Preço: {self.preco_unitario}) na Rodada {self.rodada.numero}'