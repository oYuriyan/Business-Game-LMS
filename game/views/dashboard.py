from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from game.models import JogadorPartida, Rodada, EstoqueJogador, Decisao, Partida
from django.contrib import messages
from django.shortcuts import get_object_or_404
from decimal import Decimal

@login_required
def dashboard_view(request):
    # Encontra todas as associações de partida para o jogador logado
    jogador_partidas = JogadorPartida.objects.filter(jogador=request.user).select_related('partida')
    
    info_partidas_jogador = []
    for jp in jogador_partidas:
        rodada_ativa = Rodada.objects.filter(partida=jp.partida, ativo=True).first()
        estoques = EstoqueJogador.objects.filter(jogador_partida=jp).select_related('produto')
        
        # Verifica se o jogador já tomou uma decisão para a rodada ativa
        decisao_feita = False
        if rodada_ativa:
            decisao_feita = Decisao.objects.filter(rodada=rodada_ativa, jogador=request.user).exists()

        info_partidas_jogador.append({
            'jogador_partida': jp,
            'partida': jp.partida,
            'rodada_ativa': rodada_ativa,
            'estoques': estoques,
            'decisao_feita': decisao_feita
        })

    context = {
        'info_partidas_jogador': info_partidas_jogador,
    }
    return render(request, 'dashboard.html', context)

@login_required
def lobby_view(request):
    # Busca todas as partidas que ainda não foram finalizadas
    partidas_disponiveis = Partida.objects.exclude(status='FINALIZADA').order_by('-data_inicio')
    
    # Pega as partidas que o jogador já entrou para o template saber
    partidas_do_jogador = JogadorPartida.objects.filter(jogador=request.user).values_list('partida_id', flat=True)

    context = {
        'partidas_disponiveis': partidas_disponiveis,
        'partidas_do_jogador': list(partidas_do_jogador),
    }
    return render(request, 'lobby.html', context)

@login_required
def entrar_partida_view(request, partida_id):
    partida = get_object_or_404(Partida, id=partida_id)
    
    # Evita que o jogador entre na mesma partida duas vezes
    if JogadorPartida.objects.filter(partida=partida, jogador=request.user).exists():
        messages.warning(request, 'Você já está nesta partida.')
    else:
        # Lógica para atribuir uma "Empresa" ao jogador (A, B, C, D)
        num_jogadores_atual = JogadorPartida.objects.filter(partida=partida).count()
        empresas = [
            {'nome': 'Empresa A', 'cd': 'CD Sao Paulo'},
            {'nome': 'Empresa B', 'cd': 'CD Rio de Janeiro'},
            {'nome': 'Empresa C', 'cd': 'CD Belo Horizonte'},
            {'nome': 'Empresa D', 'cd': 'CD Curitiba'},
        ]
        
        if num_jogadores_atual >= len(empresas):
            messages.error(request, 'Esta partida já está cheia.')
        else:
            empresa_designada = empresas[num_jogadores_atual]

            JogadorPartida.objects.create(
                partida=partida, 
                jogador=request.user,
                nome_empresa_jogador=empresa_designada['nome'],
                cd_origem_principal_jogador=empresa_designada['cd']
            )
            messages.success(request, f'Você entrou na partida "{partida.nome}" como {empresa_designada["nome"]}!')
    
    return redirect('dashboard')

@login_required
def tomar_decisao_view(request, rodada_id):
    rodada = get_object_or_404(Rodada, id=rodada_id, ativo=True)
    partida = rodada.partida
    # Garante que o jogador pertence a esta partida
    jogador_partida = get_object_or_404(JogadorPartida, partida=partida, jogador=request.user)

    # Impede o acesso se ele já decidiu
    if Decisao.objects.filter(rodada=rodada, jogador=request.user).exists():
        messages.warning(request, "Você já tomou sua decisão para esta rodada.")
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            qtd_produzida = int(request.POST.get('quantidade_produzida'))
            preco_venda = Decimal(request.POST.get('preco_unitario'))

            # Lógica de validação básica
            if qtd_produzida < 0 or preco_venda <= 0:
                messages.error(request, "Os valores devem ser positivos.")
            else:
                Decisao.objects.create(
                    jogador=request.user,
                    partida=partida,
                    rodada=rodada,
                    produto=rodada.produto_demandado,
                    quantidade_produzida=qtd_produzida,
                    preco_unitario=preco_venda
                )
                messages.success(request, "Sua decisão foi registrada com sucesso!")
                return redirect('dashboard')
        except (ValueError, TypeError):
            messages.error(request, "Por favor, insira valores válidos.")

    context = {
        'rodada': rodada,
        'saldo': jogador_partida.saldo
    }
    return render(request, 'tomar_decisao.html', context)