from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Partida(models.Model):
    STATUS_CHOICES = [
        ('INICIADA', 'Iniciada'),
        ('FINALIZADA', 'Finalizada'),
        ('PAUSADA', 'Pausada'),
    ]
    
    nome = models.CharField(max_length=255)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='partidas_admin')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='INICIADA')
    data_inicio = models.DateTimeField(default=timezone.now)
    data_fim = models.DateTimeField(null=True, blank=True)
    max_rodadas = models.PositiveIntegerField(default=7, help_text="Número máximo de rodadas para a partida.")
    max_jogadores = models.PositiveIntegerField(default=4, help_text="Número máximo de jogadores permitidos na partida (1-4).")
    avanco_automatico = models.BooleanField(default=False, help_text="Se verdadeiro, a rodada avança assim que o último jogador decide.")
    jogadores = models.ManyToManyField(User, through='JogadorPartida')

    def __str__(self):
        return self.nome
    
class JogadorPartida(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    jogador = models.ForeignKey(User, on_delete=models.CASCADE)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nome_empresa_jogador = models.CharField(max_length=50, null=True, blank=True, help_text="Ex: Empresa A, Empresa B...")

    class Meta:
        unique_together = ('partida', 'jogador')
    def __str__(self):
        return f"{self.jogador.username} na partida {self.partida.nome}"