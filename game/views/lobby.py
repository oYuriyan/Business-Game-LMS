from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# View do lobby — onde o jogador escolhe a partida
@login_required
def lobby_view(request):
    # Mock de partidas disponíveis (simulação)
    partidas_disponiveis = [
        {'id': 1, 'nome': 'Partida A'},
        {'id': 2, 'nome': 'Partida B'},
    ]
    return render(request, 'lobby.html', {
        'usuario': request.user,
        'partidas': partidas_disponiveis
    })