# Em: game/services/controle_rodada.py

from decimal import Decimal
from django.db import transaction
from game.models import (
    Rodada, Partida, Decisao, JogadorPartida, EstoqueJogador, Produto, CustoTransporte, CustoProducao
)
from django.utils import timezone

def todos_jogadores_decidiram(rodada: Rodada) -> bool:
    jogadores_na_partida = JogadorPartida.objects.filter(partida=rodada.partida)
    if not jogadores_na_partida.exists():
        return False # Não pode avançar se não houver jogadores
    jogadores_ids = jogadores_na_partida.values_list('jogador_id', flat=True)
    
    jogadores_que_decidiram_ids = (
        Decisao.objects
        .filter(rodada=rodada)
        .values_list('jogador_id', flat=True)
        .distinct()
    )
    return set(jogadores_ids) == set(jogadores_que_decidiram_ids)

def buscar_custo_transporte(jogador_partida: JogadorPartida, destino_rodada: str, produto_rodada: Produto) -> Decimal:
    # Retorna o custo de transporte ou um valor de penalidade muito alto se não encontrar.
    if not jogador_partida.nome_empresa_jogador or not jogador_partida.cd_origem_principal_jogador:
        return Decimal('9999.00')

    try:
        custo_obj = CustoTransporte.objects.get(
            nome_empresa_template=jogador_partida.nome_empresa_jogador,
            cd_origem=jogador_partida.cd_origem_principal_jogador,
            local_destino=destino_rodada,
            produto=produto_rodada
        )
        return custo_obj.custo_unitario_transporte
    except CustoTransporte.DoesNotExist:
        print(f"ALERTA: Custo de transporte não encontrado para {jogador_partida.nome_empresa_jogador}.")
        return Decimal('9999.00') # Penalidade

def buscar_custo_producao(jogador_partida: JogadorPartida, produto: Produto) -> Decimal:
    # Retorna o custo de produção ou um valor de penalidade muito alto se não encontrar.
    try:
        custo_obj = CustoProducao.objects.get(
            nome_empresa_template=jogador_partida.nome_empresa_jogador,
            produto=produto
        )
        return custo_obj.custo_unitario
    except CustoProducao.DoesNotExist:
        print(f"ALERTA: Custo de produção não encontrado para {jogador_partida.nome_empresa_jogador}.")
        return Decimal('9999.00') # Penalidade

def processar_rodada_atual(rodada_atual: Rodada):
    if not rodada_atual.produto_demandado or rodada_atual.quantidade_demandada is None:
        rodada_atual.resultados = {"status": "erro", "mensagem": "Demanda não definida."}
        rodada_atual.save()
        return

    resultados_rodada = {
        "demanda": {
            "produto": rodada_atual.produto_demandado.nome,
            "quantidade": rodada_atual.quantidade_demandada,
            "destino": rodada_atual.destino_demanda,
        },
        "ofertas": [],
        "vendas_realizadas": [],
        "desempenho_financeiro": [],
        "estado_final_jogadores": [],
    }

    # Fase 1: Calcular custos de produção e atualizar saldos/estoques
    for decisao_prod in Decisao.objects.filter(rodada=rodada_atual):
        jogador_partida_obj = JogadorPartida.objects.get(jogador=decisao_prod.jogador, partida=rodada_atual.partida)
        estoque_jogador, _ = EstoqueJogador.objects.get_or_create(jogador_partida=jogador_partida_obj, produto=decisao_prod.produto)
        
        custo_unitario = buscar_custo_producao(jogador_partida_obj, decisao_prod.produto)
        custo_total_producao = decisao_prod.quantidade_produzida * custo_unitario
        
        jogador_partida_obj.saldo -= custo_total_producao
        estoque_jogador.quantidade += decisao_prod.quantidade_produzida
        jogador_partida_obj.save()
        estoque_jogador.save()

    # Fase 2: Processar Vendas
    decisoes_de_venda = Decisao.objects.filter(rodada=rodada_atual, produto=rodada_atual.produto_demandado).order_by('preco_unitario', 'data_decisao')
    
    for decisao in decisoes_de_venda:
        resultados_rodada["ofertas"].append({
            "empresa": JogadorPartida.objects.get(jogador=decisao.jogador, partida=rodada_atual.partida).nome_empresa_jogador,
            "preco_ofertado": float(decisao.preco_unitario)
        })

    quantidade_restante = Decimal(rodada_atual.quantidade_demandada)
    for decisao_venda in decisoes_de_venda:
        if quantidade_restante <= 0: break
            
        jogador_partida_obj = JogadorPartida.objects.get(jogador=decisao_venda.jogador, partida=rodada_atual.partida)
        estoque_do_produto = EstoqueJogador.objects.get(jogador_partida=jogador_partida_obj, produto=rodada_atual.produto_demandado)
        
        qtd_a_vender = min(estoque_do_produto.quantidade, quantidade_restante)
        if qtd_a_vender > 0:
            custo_prod_unitario = buscar_custo_producao(jogador_partida_obj, rodada_atual.produto_demandado)
            custo_trans_unitario = buscar_custo_transporte(jogador_partida_obj, rodada_atual.destino_demanda, rodada_atual.produto_demandado)
            
            receita = qtd_a_vender * decisao_venda.preco_unitario
            custo_producao_venda = qtd_a_vender * custo_prod_unitario
            custo_transporte_venda = qtd_a_vender * custo_trans_unitario
            lucro = receita - custo_producao_venda - custo_transporte_venda
            
            jogador_partida_obj.saldo += receita - custo_transporte_venda
            estoque_do_produto.quantidade -= qtd_a_vender
            jogador_partida_obj.save()
            estoque_do_produto.save()
            
            quantidade_restante -= qtd_a_vender
            resultados_rodada["vendas_realizadas"].append({
                "empresa": jogador_partida_obj.nome_empresa_jogador,
                "quantidade": float(qtd_a_vender),
                "preco_unitario": float(decisao_venda.preco_unitario)
            })

    # Fase 3: Gerar relatórios financeiros e de estado final
    for jp in JogadorPartida.objects.filter(partida=rodada_atual.partida):
        resultados_rodada["estado_final_jogadores"].append({
            "jogador": jp.jogador.username,
            "empresa": jp.nome_empresa_jogador,
            "saldo_final": float(jp.saldo),
            "estoques": {est.produto.nome: est.quantidade for est in EstoqueJogador.objects.filter(jogador_partida=jp)}
        })

    rodada_atual.resultados = resultados_rodada
    rodada_atual.save()

@transaction.atomic
def avancar_rodada(partida: Partida) -> Rodada | None:
    rodada_atual = Rodada.objects.filter(partida=partida, ativo=True).order_by('-numero').first()
    if not rodada_atual:
        numero_nova_rodada = 1
    else:
        if not todos_jogadores_decidiram(rodada_atual):
            return None
        processar_rodada_atual(rodada_atual)
        rodada_atual.ativo = False
        rodada_atual.data_fim = timezone.now()
        rodada_atual.save()
        numero_nova_rodada = rodada_atual.numero + 1
    
    nova_rodada = Rodada.objects.create(partida=partida, numero=numero_nova_rodada, ativo=True)
    if numero_nova_rodada == 1:
        # Lógica de inicialização de saldo/estoque
        pass
    return nova_rodada

