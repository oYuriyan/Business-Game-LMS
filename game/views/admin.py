from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
from game.models import Partida, Rodada, JogadorPartida, Produto, CustoTransporte, CustoProducao, Unidade, Decisao
from game.services.controle_rodada import avancar_rodada as avancar_rodada_service
from game.dados_setup import CUSTOS_PRODUCAO_PADRAO, CUSTOS_TRANSPORTE_PADRAO
from game.models import CustoProducao, CustoTransporte, Produto

# O decorator garante que só superusuários acessem estas páginas
# Esta é a view principal do painel do admin
@user_passes_test(lambda u: u.is_superuser)
def painel_admin(request):
    partidas = Partida.objects.all().order_by('-data_inicio')
    
    partidas_info = []
    for partida in partidas:
        rodada_ativa = Rodada.objects.filter(partida=partida, ativo=True).first()
        jogadores = JogadorPartida.objects.filter(partida=partida)
        partidas_info.append({
            'partida': partida,
            'rodada_ativa': rodada_ativa,
            'jogadores': jogadores
        })

    context = {
        'partidas_info': partidas_info
    }
    return render(request, 'admin.html', context)

def popular_dados_base():
    """ Popula os custos de produção e transporte se eles não existirem. """
    
    # Popula Custos de Produção
    for empresa, produtos in CUSTOS_PRODUCAO_PADRAO.items():
        for nome_produto, custo in produtos.items():
            produto_obj, _ = Produto.objects.get_or_create(nome=nome_produto)
            CustoProducao.objects.get_or_create(
                nome_empresa_template=empresa,
                produto=produto_obj,
                defaults={'custo_unitario': custo}
            )

    # Popula Custos de Transporte
    for item in CUSTOS_TRANSPORTE_PADRAO:
        produto_obj, _ = Produto.objects.get_or_create(nome=item['produto'])
        CustoTransporte.objects.get_or_create(
            nome_empresa_template=item['empresa'],
            produto=produto_obj,
            cd_origem=item['origem'],
            local_destino=item['destino'],
            defaults={'custo_unitario_transporte': item['custo']}
        )

# View para a PÁGINA de criar uma nova partida
@user_passes_test(lambda u: u.is_superuser)
def criar_partida_view(request):
    if request.method == 'POST':
        nome_partida = request.POST.get('nome_partida')
        # Pega o valor do novo campo
        max_rodadas = request.POST.get('max_rodadas', 7) 

        if nome_partida:
            popular_dados_base()
            # Salva a partida com o número de rodadas definido
            partida = Partida.objects.create(
                nome=nome_partida,
                admin=request.user,
                max_rodadas=max_rodadas
            )
            messages.success(request, f"Partida '{partida.nome}' criada com {max_rodadas} rodadas.")
            return redirect('painel_admin')
    return render(request, 'criar_partida.html')

# View para a PÁGINA de definir a demanda de uma rodada
@user_passes_test(lambda u: u.is_superuser)
def definir_demanda_view(request, rodada_id):
    rodada = get_object_or_404(Rodada, id=rodada_id)
    produtos = Produto.objects.all()
    if request.method == 'POST':
        produto_id = request.POST.get('produto_id')
        quantidade = request.POST.get('quantidade')
        destino = request.POST.get('destino')
        
        rodada.produto_demandado_id = produto_id
        rodada.quantidade_demandada = quantidade
        rodada.destino_demanda = destino
        rodada.save()
        messages.success(request, f"Demanda para a rodada {rodada.numero} salva com sucesso.")
        return redirect('painel_admin')
        
    context = {
        'rodada': rodada,
        'produtos': produtos
    }
    return render(request, 'definir_demanda.html', context)

# View para o botao de avançar a rodada de uma partida
@user_passes_test(lambda u: u.is_superuser)
def avancar_rodada_view(request, partida_id):
    if request.method == 'POST':
        partida = get_object_or_404(Partida, id=partida_id)

        # Verifica se é a primeira rodada que está para ser iniciada
        is_first_round = not Rodada.objects.filter(partida=partida).exists()
        
        # Se for a primeira rodada, verifica a contagem de jogadores
        if is_first_round and partida.jogadorpartida_set.count() < 2:
            messages.error(request, f"Não é possível iniciar a partida '{partida.nome}' com menos de 2 jogadores.")
            return redirect('painel_admin')

        # Se a verificação passar, a lógica normal continua
        resultado_rodada = avancar_rodada_service(partida)
        
        if resultado_rodada is None:
            partida.refresh_from_db()
            if partida.status == 'FINALIZADA':
                messages.success(request, f"A última rodada foi processada e a partida '{partida.nome}' foi finalizada!")
            else:
                messages.warning(request, f"Não foi possível avançar a rodada. Verifique se todos os jogadores já tomaram suas decisões.")
        else:
            messages.success(request, f"Rodada processada. Rodada {resultado_rodada.numero} iniciada com sucesso para a partida '{partida.nome}'.")

    return redirect('painel_admin')


@user_passes_test(lambda u: u.is_superuser)
def finalizar_partida_view(request, partida_id):
    if request.method == 'POST':
        partida = get_object_or_404(Partida, id=partida_id)
        
        # Muda o status da partida para finalizada
        partida.status = 'FINALIZADA'
        partida.data_fim = timezone.now()
        partida.save()
        
        # Também desativa qualquer rodada que estivesse ativa
        Rodada.objects.filter(partida=partida, ativo=True).update(ativo=False)
        
        messages.info(request, f"A partida '{partida.nome}' foi finalizada manualmente.")
    
    return redirect('painel_admin')

@user_passes_test(lambda u: u.is_superuser)
def admin_partida_spectator_view(request, partida_id):
    partida = get_object_or_404(Partida, id=partida_id)
    rodada_ativa = Rodada.objects.filter(partida=partida, ativo=True).first()
    
    # Busca todos os jogadores da partida e suas informações
    jogadores_da_partida = JogadorPartida.objects.filter(partida=partida).order_by('nome_empresa_jogador')
    
    # Prepara uma lista com dados detalhados de cada jogador
    info_jogadores = []
    for jp in jogadores_da_partida:
        unidades = Unidade.objects.filter(jogador_partida=jp).order_by('localidade', 'produto__nome')
        decisao = Decisao.objects.filter(jogador=jp.jogador, rodada=rodada_ativa).first() if rodada_ativa else None
        
        info_jogadores.append({
            'jogador_partida': jp,
            'unidades': unidades,
            'decisao_feita': decisao is not None
        })

    context = {
        'partida': partida,
        'rodada_ativa': rodada_ativa,
        'info_jogadores': info_jogadores
    }
    return render(request, 'admin_spectator.html', context)
@user_passes_test(lambda u: u.is_superuser)
def toggle_avanco_automatico_view(request, partida_id):
    if request.method == 'POST':
        partida = get_object_or_404(Partida, id=partida_id)
        # Inverte o valor booleano atual
        partida.avanco_automatico = not partida.avanco_automatico
        partida.save()
        
        status_texto = "ativado" if partida.avanco_automatico else "desativado"
        messages.success(request, f"Avanço automático de rodada foi {status_texto} para a partida '{partida.nome}'.")
    
    return redirect('painel_admin')
    
@user_passes_test(lambda u: u.is_superuser)
def excluir_partida_view(request, partida_id):
    # Apenas aceita requisições POST para segurança
    if request.method == 'POST':
        partida = get_object_or_404(Partida, id=partida_id)
        partida.delete()
        messages.success(request, f"A partida '{partida.nome}' foi excluída com sucesso.")
    return redirect('painel_admin')