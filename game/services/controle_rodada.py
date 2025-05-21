from game.models.rodada import Rodada
from game.models.partida import Partida
from game.models.decisao import Decisao
from django.utils import timezone
from django.db import transaction

"""
Módulo de controle de rodadas.

Responsável por iniciar, encerrar e avançar rodadas de uma partida.
Pode ser chamado tanto pelo admin quanto por eventos automáticos no futuro.
"""

def todos_jogadores_decidiram(rodada: Rodada) -> bool:
    jogadores = rodada.partida.jogadores.all()
    jogadores_que_decidiram = (
        Decisao.objects
        .filter(rodada=rodada)
        .values_list('jogador_id', flat=True)
        .distinct()
    )
    return set(jogadores.values_list('id', flat=True)) == set(jogadores_que_decidiram)

@transaction.atomic
def avancar_rodada(partida: Partida) -> Rodada | None:
    """
    Encerra a rodada atual (se todos os jogadores tiverem decidido) e cria uma nova.

    Retorna a nova rodada criada ou None caso a rodada atual ainda esteja incompleta.
    """
    rodada_atual = Rodada.objects.filter(partida=partida, ativo=True).order_by('-numero').first()

    if not rodada_atual:
        numero = 1
    else:
        if not todos_jogadores_decidiram(rodada_atual):
            return None  # ainda não pode avançar

        rodada_atual.ativo = False
        rodada_atual.data_fim = timezone.now()
        rodada_atual.save()
        numero = rodada_atual.numero + 1

    nova_rodada = Rodada.objects.create(
        partida=partida,
        numero=numero,
        ativo=True,
        data_inicio=timezone.now()
    )
    
    return nova_rodada