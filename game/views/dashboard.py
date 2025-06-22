from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from game.models import JogadorPartida, Rodada, Unidade, Decisao, Partida, Produto, CustoProducao, CustoTransporte
from game.services.controle_rodada import avancar_rodada as avancar_rodada_service, todos_jogadores_decidiram
from django.contrib import messages
from django.shortcuts import get_object_or_404
from decimal import Decimal

@login_required
def dashboard_view(request):
    # Encontra todas as associações de partida para o jogador logado
    jogador_partidas = JogadorPartida.objects.filter(
        jogador=request.user
    ).exclude(partida__status='FINALIZADA').select_related('partida')
    
    info_partidas_jogador = []
    for jp in jogador_partidas:
        rodada_ativa = Rodada.objects.filter(partida=jp.partida, ativo=True).first()
        estoques = Unidade.objects.filter(jogador_partida=jp).select_related('produto')
        
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
    partidas_disponiveis = Partida.objects.exclude(status='FINALIZADA').order_by('-data_inicio')
    partidas_do_jogador = JogadorPartida.objects.filter(jogador=request.user).values_list('partida_id', flat=True)

    context = {
        'partidas_disponiveis': partidas_disponiveis,
        'partidas_do_jogador': list(partidas_do_jogador),
    }
    return render(request, 'lobby.html', context)

# Dados das tabelas para o setup inicial das empresas
EMPRESAS_SETUP = {
    'Empresa A': {
        'Cafeteira': {'Unidade 1': 100, 'Unidade 2': 80, 'Unidade 3': 50},
        'Torradeira': {'Unidade 1': 80, 'Unidade 2': 50, 'Unidade 3': 40},
    },
    'Empresa B': {
        'Cafeteira': {'Unidade 1': 100, 'Unidade 2': 80, 'Unidade 3': 50},
        'Torradeira': {'Unidade 1': 80, 'Unidade 2': 50, 'Unidade 3': 40},
    },
    'Empresa C': {
        'Cafeteira': {'Unidade 1': 100, 'Unidade 2': 80, 'Unidade 3': 50},
        'Torradeira': {'Unidade 1': 80, 'Unidade 2': 50, 'Unidade 3': 40},
    },
    'Empresa D': {
        'Cafeteira': {'Unidade 1': 100, 'Unidade 2': 80, 'Unidade 3': 50},
        'Torradeira': {'Unidade 1': 80, 'Unidade 2': 50, 'Unidade 3': 40},
    }
}

@login_required
def entrar_partida_view(request, partida_id):
    partida = get_object_or_404(Partida, id=partida_id)
    partida_para_entrar = get_object_or_404(Partida, id=partida_id)
    partidas_ativas_do_jogador = JogadorPartida.objects.filter(
        jogador=request.user
    ).exclude(partida__status='FINALIZADA').exclude(partida=partida_para_entrar)

    if partidas_ativas_do_jogador.exists():
        messages.error(request, 'Você já está em uma partida ativa. Saia da partida atual para poder entrar em uma nova.')
        return redirect('lobby')
    
    if JogadorPartida.objects.filter(partida=partida_para_entrar, jogador=request.user).exists():
        messages.warning(request, 'Você já está nesta partida.')
    else:
        num_jogadores_atual = JogadorPartida.objects.filter(partida=partida_para_entrar).count()
        empresas_disponiveis = ['Empresa A', 'Empresa B', 'Empresa C', 'Empresa D']
        
        if num_jogadores_atual >= len(empresas_disponiveis):
            messages.error(request, 'Esta partida já está cheia.')
        else:
            nome_empresa_designada = empresas_disponiveis[num_jogadores_atual]

            # Cria a associação JogadorPartida
            jp = JogadorPartida.objects.create(
                partida=partida_para_entrar, 
                jogador=request.user,
                nome_empresa_jogador=nome_empresa_designada
            )

            # Popula as Unidades e estoques iniciais para o jogador
            if nome_empresa_designada in EMPRESAS_SETUP:
                setup_empresa = EMPRESAS_SETUP[nome_empresa_designada]
                for nome_produto, unidades in setup_empresa.items():
                    try:
                        produto = Produto.objects.get(nome=nome_produto)
                        for nome_unidade, estoque_inicial in unidades.items():
                            Unidade.objects.create(
                                jogador_partida=jp,
                                produto=produto,
                                localidade=nome_unidade,
                                quantidade=estoque_inicial
                            )
                    except Produto.DoesNotExist:
                        messages.error(request, f"O produto base '{nome_produto}' não foi encontrado no sistema.")
            
            messages.success(request, f'Você entrou na partida "{partida_para_entrar.nome}" como {nome_empresa_designada}!')
    
    return redirect('dashboard')

@login_required
def partida_detalhe_view(request, partida_id):
    partida = get_object_or_404(Partida, id=partida_id)
    jogador_partida = get_object_or_404(JogadorPartida, partida=partida, jogador=request.user)
    rodada_ativa = Rodada.objects.filter(partida=partida, ativo=True).first()

    # Lógica de tomada de decisão (o seu código, com o redirect corrigido)
    if request.method == 'POST' and rodada_ativa:
        try:
            unidade_id = request.POST.get('unidade_origem_id')
            qtd_produzida = int(request.POST.get('quantidade_produzida', 0))
            preco_venda = Decimal(request.POST.get('preco_unitario'))

            if not unidade_id:
                messages.error(request, "Você deve selecionar uma Unidade de Origem.")
            else:
                unidade_selecionada = get_object_or_404(Unidade, id=unidade_id, jogador_partida=jogador_partida)
                if unidade_selecionada.produto != rodada_ativa.produto_demandado:
                    messages.error(request, "A unidade selecionada não corresponde ao produto demandado.")
                else:
                    Decisao.objects.create(
                        jogador=request.user, partida=partida, rodada=rodada_ativa,
                        produto=rodada_ativa.produto_demandado, unidade_origem=unidade_selecionada,
                        quantidade_produzida=qtd_produzida, preco_unitario=preco_venda
                    )
                    messages.success(request, "Sua decisão para a rodada foi registrada com sucesso!")
                    partida.refresh_from_db() 
                    if partida.avanco_automatico:
                        # Re-checa se todos decidiram apos a decisão atual ser salva.
                        if todos_jogadores_decidiram(rodada_ativa):
                            messages.info(request, "Todos os jogadores decidiram. A rodada será avançada automaticamente.")
                            avancar_rodada_service(partida)
                    return redirect('partida_detalhe', partida_id=partida.id)
        except (ValueError, TypeError):
            messages.error(request, "Por favor, insira valores válidos.")

    # Busca de dados para exibir na página
    unidades_do_jogador = Unidade.objects.filter(jogador_partida=jogador_partida).order_by('localidade', 'produto__nome')
    decisao_feita = False
    unidades_para_decisao = []
    if rodada_ativa:
        decisao_feita = Decisao.objects.filter(rodada=rodada_ativa, jogador=request.user).exists()
        unidades_para_decisao = unidades_do_jogador.filter(produto=rodada_ativa.produto_demandado)
    
    ultima_rodada_finalizada = Rodada.objects.filter(partida=partida, ativo=False).order_by('-numero').first()

    nome_empresa = jogador_partida.nome_empresa_jogador
    custos_producao = CustoProducao.objects.filter(nome_empresa_template=nome_empresa).order_by('produto__nome')
    custos_transporte_raw = CustoTransporte.objects.filter(nome_empresa_template=nome_empresa).order_by('cd_origem', 'local_destino')

    # Agrupando custos de transporte por unidade de origem para exibição limpa
    custos_transporte_agrupados = {}
    for custo in custos_transporte_raw:
        if custo.cd_origem not in custos_transporte_agrupados:
            custos_transporte_agrupados[custo.cd_origem] = []
        custos_transporte_agrupados[custo.cd_origem].append(custo)
    
    context = {
        'partida': partida,
        'jogador_partida': jogador_partida,
        'rodada_ativa': rodada_ativa,
        'unidades_do_jogador': unidades_do_jogador,
        'decisao_feita': decisao_feita,
        'unidades_para_decisao': unidades_para_decisao,
        'ultima_rodada_finalizada': ultima_rodada_finalizada,
        'custos_producao': custos_producao,
        'custos_transporte': custos_transporte_agrupados,
    }
    return render(request, 'partida_detalhe.html', context)

@login_required
def resultados_rodada_view(request, rodada_id):
    rodada = get_object_or_404(Rodada, id=rodada_id)
    # Garante que o jogador pertence à partida desta rodada
    get_object_or_404(JogadorPartida, partida=rodada.partida, jogador=request.user)
    
    # Busca todas as decisões daquela rodada para mostrar o "pregão"
    decisoes_da_rodada = Decisao.objects.filter(rodada=rodada).select_related('jogador', 'produto').order_by('preco_unitario')
    
    # Os resultados já foram calculados e salvos no campo JSON da rodada
    resultados = rodada.resultados
    
    context = {
        'rodada': rodada,
        'decisoes': decisoes_da_rodada,
        'resultados': resultados
    }
    
    return render(request, 'resultados_rodada.html', context)

@login_required
def reabastecer_estoque_view(request, estoque_id):
    # Garante que a ação seja feita por um POST para segurança
    if request.method == 'POST':
        estoque = get_object_or_404(Unidade, id=estoque_id)
        jogador_partida = estoque.jogador_partida

        # Verifica se o jogador logado é o dono deste estoque
        if jogador_partida.jogador != request.user:
            messages.error(request, "Você não tem permissão para realizar esta ação.")
            return redirect('dashboard')

        CUSTO_REABASTECIMENTO = Decimal('5000.00')
        QUANTIDADE_REABASTECIDA = 100 # Estoque volta para 100 unidades

        if estoque.quantidade > 0:
            messages.warning(request, "Você só pode reabastecer itens com estoque zerado.")
        elif jogador_partida.saldo < CUSTO_REABASTECIMENTO:
            messages.error(request, f"Saldo insuficiente. Você precisa de R$ {CUSTO_REABASTECIMENTO} para reabastecer.")
        else:
            jogador_partida.saldo -= CUSTO_REABASTECIMENTO
            estoque.quantidade = QUANTIDADE_REABASTECIDA
            
            jogador_partida.save()
            estoque.save()
            
            messages.success(request, f"Estoque de {estoque.produto.nome} reabastecido com sucesso!")
    
    # Redireciona de volta para o dashboard em qualquer caso
    return redirect('dashboard')

@login_required
def game_state_api(request, partida_id):
    """
    Uma view de API que retorna o estado atual do jogo em formato JSON.
    """
    partida = get_object_or_404(Partida, id=partida_id)
    jogador_partida = get_object_or_404(JogadorPartida, partida=partida, jogador=request.user)
    rodada_ativa = Rodada.objects.filter(partida=partida, ativo=True).first()

    # Prepara os dados para serem enviados como JSON
    data = {
        'saldo': float(jogador_partida.saldo),
        'rodada_ativa': None,
        'decisao_feita': False,
        'estoques': {}
    }

    if rodada_ativa:
        data['rodada_ativa'] = {
            'numero': rodada_ativa.numero,
            'demanda_produto': rodada_ativa.produto_demandado.nome if rodada_ativa.produto_demandado else None,
            'demanda_quantidade': rodada_ativa.quantidade_demandada,
            'demanda_destino': rodada_ativa.destino_demanda,
        }
        data['decisao_feita'] = Decisao.objects.filter(rodada=rodada_ativa, jogador=request.user).exists()
    
    unidades = Unidade.objects.filter(jogador_partida=jogador_partida)
    for unidade in unidades:
        data['estoques'][f"{unidade.produto.nome} ({unidade.localidade})"] = unidade.quantidade
    
    return JsonResponse(data)

@login_required
def resultados_finais_view(request, partida_id):
    partida = get_object_or_404(Partida, id=partida_id, status='FINALIZADA')
    
    # Garante que o jogador que está acessando pertence à partida
    get_object_or_404(JogadorPartida, partida=partida, jogador=request.user)

    # Busca todos os jogadores da partida e ordena pelo saldo final em ordem decrescente
    jogadores_classificacao = JogadorPartida.objects.filter(partida=partida).order_by('-saldo')

    context = {
        'partida': partida,
        'ranking': jogadores_classificacao
    }
    return render(request, 'resultados_finais.html', context)