# Em: game/services/controle_rodada.py

from decimal import Decimal
from django.db import transaction
from game.models import (
    Rodada, Partida, Decisao, JogadorPartida, Unidade, Produto, CustoTransporte, CustoProducao
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

def buscar_custo_transporte(jogador_partida: JogadorPartida, destino_rodada: str, produto_rodada: Produto, origem_unidade: str) -> Decimal:
    try:
        custo_obj = CustoTransporte.objects.get(
            nome_empresa_template=jogador_partida.nome_empresa_jogador,
            cd_origem=origem_unidade, # USA A ORIGEM DA UNIDADE ESCOLHIDA
            local_destino=destino_rodada,
            produto=produto_rodada
        )
        return custo_obj.custo_unitario_transporte
    except CustoTransporte.DoesNotExist:
        print(f"ALERTA: Custo de transporte não encontrado.")
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

    # FASE 1:
    for decisao_prod in Decisao.objects.filter(rodada=rodada_atual):
        jogador_partida_obj = JogadorPartida.objects.get(jogador=decisao_prod.jogador, partida=rodada_atual.partida)
        
        # Pega a unidade exata que o jogador usou para tomar a decisão.
        unidade_de_producao = decisao_prod.unidade_origem

        # A produção só afeta o produto da unidade escolhida.
        if decisao_prod.quantidade_produzida > 0:
            custo_unitario = buscar_custo_producao(jogador_partida_obj, unidade_de_producao.produto)
            custo_total_producao = decisao_prod.quantidade_produzida * custo_unitario
            
            # Debita o saldo do jogador
            jogador_partida_obj.saldo -= custo_total_producao
            # Adiciona o estoque na unidade correta
            unidade_de_producao.quantidade += decisao_prod.quantidade_produzida
            
            jogador_partida_obj.save()
            unidade_de_producao.save()

    # FASE 2: Processar Vendas
    decisoes_de_venda = Decisao.objects.filter(rodada=rodada_atual, produto=rodada_atual.produto_demandado).order_by('preco_unitario', 'data_decisao')
    
    for decisao in decisoes_de_venda:
        jp_oferta = JogadorPartida.objects.get(jogador=decisao.jogador, partida=rodada_atual.partida)
        resultados_rodada["ofertas"].append({
            "empresa": jp_oferta.nome_empresa_jogador,
            "preco_ofertado": float(decisao.preco_unitario)
        })

    quantidade_restante = Decimal(rodada_atual.quantidade_demandada)
    for decisao_venda in decisoes_de_venda:
        if quantidade_restante <= 0: break
            
        jogador_partida_obj = JogadorPartida.objects.get(jogador=decisao_venda.jogador, partida=rodada_atual.partida)
        unidade_de_origem = decisao_venda.unidade_origem
        estoque_disponivel_na_unidade = unidade_de_origem.quantidade
        
        if estoque_disponivel_na_unidade <= 0: continue
        
        qtd_a_vender = min(estoque_disponivel_na_unidade, quantidade_restante)
        
        if qtd_a_vender > 0:
            custo_prod_unitario = buscar_custo_producao(jogador_partida_obj, rodada_atual.produto_demandado)
            custo_trans_unitario = buscar_custo_transporte(
                jogador_partida_obj, 
                rodada_atual.destino_demanda, 
                rodada_atual.produto_demandado,
                unidade_de_origem.localidade
            )
            
            receita = qtd_a_vender * decisao_venda.preco_unitario
            custo_transporte_venda = qtd_a_vender * custo_trans_unitario
            
            jogador_partida_obj.saldo += receita - custo_transporte_venda
            unidade_de_origem.quantidade -= qtd_a_vender
            
            jogador_partida_obj.save()
            unidade_de_origem.save()
            
            quantidade_restante -= qtd_a_vender
            resultados_rodada["vendas_realizadas"].append({
                "empresa": jogador_partida_obj.nome_empresa_jogador,
                "origem": unidade_de_origem.localidade,
                "quantidade": float(qtd_a_vender),
                "preco_unitario": float(decisao_venda.preco_unitario)
            })

    # FASE 3: Gerar relatórios
    for jp in JogadorPartida.objects.filter(partida=rodada_atual.partida):
        resultados_rodada["estado_final_jogadores"].append({
            "jogador": jp.jogador.username,
            "empresa": jp.nome_empresa_jogador,
            "saldo_final": float(jp.saldo),
            "estoques": {
                f"{est.produto.nome} ({est.localidade})": est.quantidade 
                for est in Unidade.objects.filter(jogador_partida=jp)
            }
        })

    rodada_atual.resultados = resultados_rodada
    rodada_atual.save()

@transaction.atomic
def avancar_rodada(partida: Partida) -> Rodada | None:
    # 1. Primeiro, encontra se há uma rodada ativa que precisa ser processada.
    rodada_ativa_para_processar = Rodada.objects.filter(partida=partida, ativo=True).first()

    # 2. Se houver uma rodada ativa, processa e desativa ela.
    if rodada_ativa_para_processar:
        if not todos_jogadores_decidiram(rodada_ativa_para_processar):
            return None
        
        processar_rodada_atual(rodada_ativa_para_processar)
        rodada_ativa_para_processar.ativo = False
        rodada_ativa_para_processar.data_fim = timezone.now()
        rodada_ativa_para_processar.save()

    # 3. Descobre qual é o número da próxima rodada olhando a última rodada criada,
    #    seja ela ativa ou não, evita a criação de duplicatas.
    ultima_rodada_criada = Rodada.objects.filter(partida=partida).order_by('-numero').first()
    proximo_numero_rodada = (ultima_rodada_criada.numero + 1) if ultima_rodada_criada else 1

    # 4. Verifica se o jogo deve terminar antes de criar uma nova rodada.
    if partida.max_rodadas and proximo_numero_rodada > partida.max_rodadas:
        partida.status = 'FINALIZADA'
        partida.data_fim = timezone.now()
        partida.save()
        return None # Retorna None para indicar que o jogo acabou.

    # 5. Se o jogo não acabou, cria a nova rodada.
    nova_rodada = Rodada.objects.create(
        partida=partida,
        numero=proximo_numero_rodada,
        ativo=True,
    )
    
    return nova_rodada