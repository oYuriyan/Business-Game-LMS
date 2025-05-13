from game.models.rodada import Rodada
from game.models.partida import Partida
from django.utils import timezone
from django.db import transaction

"""
Módulo de controle de rodadas.

Responsável por iniciar, encerrar e avançar rodadas de uma partida.
Pode ser chamado tanto pelo admin quanto por eventos automáticos no futuro.
"""

@transaction.atomic  # Garante que as ações abaixo aconteçam todas juntas (evita corrupção)
def avancar_rodada(partida: Partida) -> Rodada:
    """
    Encerra a rodada atual (se houver) e cria uma nova rodada na partida.

    Parâmetros:
    - partida (Partida): instância da partida que terá sua rodada avançada

    Retorna:
    - nova_rodada (Rodada): instância da nova rodada criada
    """

    # Busca a rodada atual ativa
    rodada_atual = Rodada.objects.filter(partida=partida, ativa=True).order_by('-numero').first()

    if rodada_atual:
        rodada_atual.ativa = False  # Encerra a rodada atual
        rodada_atual.save()

        proximo_numero = rodada_atual.numero + 1
    else:
        # Se for a primeira rodada
        proximo_numero = 1

    # Cria a nova rodada
    nova_rodada = Rodada.objects.create(
        partida=partida,
        numero=proximo_numero,
        ativa=True,
        data_inicio=timezone.now()
    )

    # (futuro): disparar eventos de início de rodada, resetar dados temporários etc.

    return nova_rodada
