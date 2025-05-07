from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from game.models import Partida

@login_required
def dashboard_view(request):
    
    #Exibe a tela inicial após login, com acesso ao Lobby.
    
    return render(request, 'dashboard.html', {
        'usuario': request.user,
        'mensagem': 'Bem-vindo ao Business Game!'
    })


@login_required
def lobby_view(request):
    #Tela onde o usuário visualiza as partidas disponíveis e pode criar novas.   

    # Criação de nova partida
    if request.method == "POST":
        nome = request.POST.get("nome_partida")
        if nome:
            Partida.objects.create(nome=nome, ativa=True)

    # Lista de partidas ativas
    partidas = Partida.objects.filter(ativa=True).order_by('-data_criacao')

    return render(request, 'lobby.html', {
        'usuario': request.user,
        'partidas': partidas
    })