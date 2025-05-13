from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from .rodada import Rodada
from .partida import Partida

class Decisao(models.Model):
    jogador = models.ForeignKey(User, on_delete=models.CASCADE)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    rodada = models.ForeignKey(Rodada, on_delete=models.CASCADE, related_name='decisoes')
    produto = models.CharField(max_length=50)  # Ex: 'cafeteira', 'torradeira'
    quantidade_produzida = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    distribuicao = models.JSONField(default=dict)  # Ex: {"Cliente A": 30, "Cliente B": 20}
    
    custo_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    data_decisao = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('jogador', 'rodada', 'produto')  # 1 decisão por produto por rodada

    def __str__(self):
        return f'{self.jogador.username} - {self.produto} (Qtd: {self.quantidade_produzida})'