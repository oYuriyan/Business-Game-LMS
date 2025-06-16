from decimal import Decimal
from django.db import transaction
from game.models import (
    Rodada, Partida, Decisao, JogadorPartida, EstoqueJogador, Produto, CustoTransporte
)
from django.utils import timezone

def todos_jogadores_decidiram(rodada: Rodada) -> bool:
    jogadores_na_partida = JogadorPartida.objects.filter(partida=rodada.partida)
    jogadores_ids = jogadores_na_partida.values_list('jogador_id', flat=True)
    
    jogadores_que_decidiram_ids = (
        Decisao.objects
        .filter(rodada=rodada)
        .values_list('jogador_id', flat=True)
        .distinct()
    )
    return set(jogadores_ids) == set(jogadores_que_decidiram_ids)

def buscar_custo_transporte(jogador_partida: JogadorPartida, destino_rodada: str, produto_rodada: Produto) -> Decimal | None:
    if not jogador_partida.nome_empresa_jogador or not jogador_partida.cd_origem_principal_jogador:
        return None

    try:
        custo_obj = CustoTransporte.objects.get(
            nome_empresa_template=jogador_partida.nome_empresa_jogador,
            cd_origem=jogador_partida.cd_origem_principal_jogador,
            local_destino=destino_rodada,
            produto=produto_rodada
        )
        return custo_obj.custo_unitario_transporte
    except CustoTransporte.DoesNotExist:
        print(f"ALERTA: Custo de transporte não encontrado para {jogador_partida.nome_empresa_jogador} de {jogador_partida.cd_origem_principal_jogador} para {destino_rodada} do produto {produto_rodada.nome}")
        return None
    except Exception as e:
        print(f"Erro ao buscar custo de transporte: {e}")
        return None

def processar_rodada_atual(rodada_atual: Rodada):
    if not rodada_atual.produto_demandado or rodada_atual.quantidade_demandada is None:
        print(f"Rodada {rodada_atual.numero} não pode ser processada: demanda não definida.")
        rodada_atual.resultados = {"status": "erro", "mensagem": "Demanda não definida."}
        rodada_atual.save()
        return

    resultados_rodada = {
        "produto_demandado": rodada_atual.produto_demandado.nome,
        "quantidade_total_demandada": rodada_atual.quantidade_demandada,
        "destino": rodada_atual.destino_demanda,
        "producao_e_custos": [],
        "vendas_realizadas": [],
        "erros_processamento": [],
        "estado_final_jogadores": []
    }

    decisoes_de_producao_da_rodada = Decisao.objects.filter(rodada=rodada_atual)
    for decisao_prod in decisoes_de_producao_da_rodada:
        jogador_partida_obj = JogadorPartida.objects.get(jogador=decisao_prod.jogador, partida=rodada_atual.partida)
        estoque_jogador, _ = EstoqueJogador.objects.get_or_create(jogador_partida=jogador_partida_obj, produto=decisao_prod.produto)
        custo_para_produzir = Decimal('0.00')
        if decisao_prod.quantidade_produzida > 0:
            custo_para_produzir = decisao_prod.quantidade_produzida * decisao_prod.produto.custo_producao_unitario
            jogador_partida_obj.saldo -= custo_para_produzir
            estoque_jogador.quantidade += decisao_prod.quantidade_produzida
            jogador_partida_obj.save()
            estoque_jogador.save()
        resultados_rodada["producao_e_custos"].append({"jogador": decisao_prod.jogador.username, "produto_produzido": decisao_prod.produto.nome, "quantidade_produzida": decisao_prod.quantidade_produzida, "custo_de_producao_incorridos": float(custo_para_produzir)})

    decisoes_de_venda_para_demanda = Decisao.objects.filter(rodada=rodada_atual, produto=rodada_atual.produto_demandado).order_by('preco_unitario', 'data_decisao')
    quantidade_restante_demanda = Decimal(rodada_atual.quantidade_demandada)
    for decisao_venda in decisoes_de_venda_para_demanda:
        if quantidade_restante_demanda <= 0:
            break
        jogador_partida_obj = JogadorPartida.objects.get(jogador=decisao_venda.jogador, partida=rodada_atual.partida)
        estoque_do_produto_demandado = EstoqueJogador.objects.get(jogador_partida=jogador_partida_obj, produto=rodada_atual.produto_demandado)
        quantidade_ofertada_real = estoque_do_produto_demandado.quantidade
        if quantidade_ofertada_real <= 0:
            continue
        quantidade_a_vender = min(quantidade_ofertada_real, quantidade_restante_demanda)
        if quantidade_a_vender > 0:

            custo_transporte_unitario = buscar_custo_transporte(
                jogador_partida=jogador_partida_obj,
                destino_rodada=rodada_atual.destino_demanda,
                produto_rodada=rodada_atual.produto_demandado
            ) or Decimal('999.00')

            receita_venda = quantidade_a_vender * decisao_venda.preco_unitario
            custo_producao_dos_vendidos = quantidade_a_vender * decisao_venda.produto.custo_producao_unitario
            custo_transporte_venda = quantidade_a_vender * custo_transporte_unitario
            lucro_liquido_da_venda = receita_venda - custo_producao_dos_vendidos - custo_transporte_venda
            
            jogador_partida_obj.saldo += receita_venda - custo_transporte_venda
            estoque_do_produto_demandado.quantidade -= quantidade_a_vender
            jogador_partida_obj.save()
            estoque_do_produto_demandado.save()
            decisao_venda.custo_total = custo_producao_dos_vendidos + custo_transporte_venda
            decisao_venda.save()

            quantidade_restante_demanda -= quantidade_a_vender
            resultados_rodada["vendas_realizadas"].append({"jogador": decisao_venda.jogador.username, "quantidade_vendida": float(quantidade_a_vender), "preco_unitario_venda": float(decisao_venda.preco_unitario), "lucro_liquido_desta_venda": float(lucro_liquido_da_venda)})
    
    for jp in JogadorPartida.objects.filter(partida=rodada_atual.partida):
        resultados_rodada["estado_final_jogadores"].append({"jogador": jp.jogador.username, "saldo_final": float(jp.saldo), "estoques": {est.produto.nome: est.quantidade for est in EstoqueJogador.objects.filter(jogador_partida=jp)}})
    rodada_atual.resultados = resultados_rodada
    rodada_atual.save()
    print("Processamento da rodada concluído.")


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
        produtos_disponiveis = Produto.objects.all()
        jogadores_da_partida = JogadorPartida.objects.filter(partida=partida)
        for jogador_p in jogadores_da_partida:
            jogador_p.saldo = Decimal('20000.00')
            jogador_p.save()
            for produto_base in produtos_disponiveis:
                EstoqueJogador.objects.update_or_create(jogador_partida=jogador_p, produto=produto_base, defaults={'quantidade': 100})
    return nova_rodada