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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='INICIADA')
    data_inicio = models.DateTimeField(default=timezone.now)
    data_fim = models.DateTimeField(null=True, blank=True)
    
    # Relacionamento com usuários (jogadores)
    jogadores = models.ManyToManyField(User, through='JogadorPartida')

    def __str__(self):
        return self.nome
    
class JogadorPartida(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    jogador = models.ForeignKey(User, on_delete=models.CASCADE)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.jogador.username} na partida {self.partida.nome}"