from game.models import Rodada, Partida, Decisao, JogadorPartida, EstoqueJogador, Produto
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

"""
Módulo de controle de rodadas.

Responsável por iniciar, encerrar e avançar rodadas de uma partida.
Pode ser chamado tanto pelo admin quanto por eventos automáticos no futuro.
"""

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
        "vendas_realizadas": [],
        "producao_e_custos": [], # Para registrar o que foi produzido e os custos associados
        "erros_processamento": []
    }

    # Fase 1: Processar Produção e Custos de Produção para TODOS os jogadores que decidiram produzir
    # Os jogadores primeiro decidem quanto produzir do produto em foco (ou de todos os produtos que eles podem fabricar)
    # Para esta rodada, vamos assumir que Decisao.produto é o produto que o jogador está focando para a demanda,
    # mas Decisao.quantidade_produzida é o que ele FABRICA dele.

    decisoes_de_producao_da_rodada = Decisao.objects.filter(rodada=rodada_atual) # Pegar todas as decisões

    for decisao_prod in decisoes_de_producao_da_rodada:
        jogador_partida_obj = JogadorPartida.objects.get(jogador=decisao_prod.jogador, partida=rodada_atual.partida)
        estoque_jogador, created = EstoqueJogador.objects.get_or_create(
            jogador_partida=jogador_partida_obj,
            produto=decisao_prod.produto, # O produto que ele decidiu produzir
            defaults={'quantidade': 0}
        )

        custo_para_produzir = Decimal('0.00')
        if decisao_prod.quantidade_produzida > 0:
            custo_para_produzir = decisao_prod.quantidade_produzida * decisao_prod.produto.custo_producao_unitario
            
            # Deduz o custo de produção do saldo do jogador
            jogador_partida_obj.saldo -= custo_para_produzir
            jogador_partida_obj.save()

            # Adiciona ao estoque do jogador o que foi produzido
            estoque_jogador.quantidade += decisao_prod.quantidade_produzida
            estoque_jogador.save()
        
        resultados_rodada["producao_e_custos"].append({
            "jogador": decisao_prod.jogador.username,
            "produto_produzido": decisao_prod.produto.nome,
            "quantidade_produzida": decisao_prod.quantidade_produzida,
            "custo_de_producao_incorridos": float(custo_para_produzir),
            "saldo_atual": float(jogador_partida_obj.saldo),
            "estoque_atual_do_produto": estoque_jogador.quantidade
        })


    # Fase 2: Processar Vendas com base na demanda da rodada e estoque agora atualizado
    # Apenas para o produto_demandado pela rodada
    decisoes_de_venda_para_demanda = Decisao.objects.filter(
        rodada=rodada_atual, 
        produto=rodada_atual.produto_demandado # Filtra decisões APENAS para o produto que o admin demandou
    ).order_by('preco_unitario', 'data_decisao') # Ordena por menor preço, depois por quem decidiu primeiro

    quantidade_restante_demanda = Decimal(rodada_atual.quantidade_demandada) # Usar Decimal para consistência

    for decisao_venda in decisoes_de_venda_para_demanda:
        if quantidade_restante_demanda <= 0:
            break # Demanda já atendida

        jogador_partida_obj = JogadorPartida.objects.get(jogador=decisao_venda.jogador, partida=rodada_atual.partida)
        
        # Pega o estoque ATUALIZADO do jogador para o produto demandado
        try:
            estoque_do_produto_demandado = EstoqueJogador.objects.get(
                jogador_partida=jogador_partida_obj,
                produto=rodada_atual.produto_demandado
            )
        except EstoqueJogador.DoesNotExist:
            # Se não tem registro de estoque, significa que ele não produziu este item.
            resultados_rodada["erros_processamento"].append({
                "jogador": decisao_venda.jogador.username,
                "mensagem": f"Tentou vender {rodada_atual.produto_demandado.nome} sem ter produzido/estoque."
            })
            continue # Próxima decisão

        # O jogador oferta o preço (Decisao.preco_unitario).
        # A quantidade que ele PODE vender é o que ele tem em ESTOQUE.
        # A `Decisao.quantidade_produzida` já foi usada para fabricar e atualizar o estoque.
        # Para a VENDA, o que limita é o estoque real.

        quantidade_ofertada_real_pelo_jogador = estoque_do_produto_demandado.quantidade 
        
        if quantidade_ofertada_real_pelo_jogador <= 0:
            continue # Não tem o produto em estoque para vender, embora tenha feito uma "decisão de venda"

        quantidade_a_vender = min(quantidade_ofertada_real_pelo_jogador, quantidade_restante_demanda)

        if quantidade_a_vender > 0:
            # Custo de Transporte (vamos buscar na nova tabela depois)
            # Por agora, um placeholder ou um valor do Produto se existir
            custo_transporte_unitario = buscar_custo_transporte(
                origem="CD_JOGADOR_" + str(jogador_partida_obj.id), # Representa a "empresa" ou CD do jogador
                destino=rodada_atual.destino_demanda,
                produto=rodada_atual.produto_demandado
            )
            if custo_transporte_unitario is None: # Fallback se não encontrar custo específico
                custo_transporte_unitario = Decimal('3.00') # Valor padrão de fallback
                resultados_rodada["erros_processamento"].append({
                    "jogador": decisao_venda.jogador.username,
                    "mensagem": f"Custo de transporte não encontrado para {rodada_atual.produto_demandado.nome} para {rodada_atual.destino_demanda}. Usado fallback."
                })


            receita_venda = quantidade_a_vender * decisao_venda.preco_unitario
            # O custo de produção já foi debitado do saldo na Fase 1.
            # Para o cálculo do lucro DA VENDA, precisamos considerá-lo, mas não debitar de novo.
            # O custo que entra na `Decisao.custo_total` é o custo do produto vendido + transporte.
            custo_producao_dos_vendidos = quantidade_a_vender * decisao_venda.produto.custo_producao_unitario # Custo do que foi efetivamente vendido
            custo_transporte_venda = quantidade_a_vender * custo_transporte_unitario
            
            lucro_liquido_da_venda = receita_venda - custo_producao_dos_vendidos - custo_transporte_venda
            
            # Adicionar receita ao saldo do jogador
            jogador_partida_obj.saldo += receita_venda
            # Deduzir custo de transporte do saldo do jogador
            jogador_partida_obj.saldo -= custo_transporte_venda
            jogador_partida_obj.save()

            # Deduzir do estoque do jogador o que foi vendido
            estoque_do_produto_demandado.quantidade -= quantidade_a_vender
            estoque_do_produto_demandado.save()

            # Salva o custo total (produção dos itens vendidos + transporte) na decisão
            decisao_venda.custo_total = custo_producao_dos_vendidos + custo_transporte_venda
            decisao_venda.save()

            quantidade_restante_demanda -= quantidade_a_vender

            resultados_rodada["vendas_realizadas"].append({
                "jogador": decisao_venda.jogador.username,
                "produto": decisao_venda.produto.nome,
                "quantidade_vendida": float(quantidade_a_vender),
                "preco_unitario_venda": float(decisao_venda.preco_unitario),
                "receita_bruta_venda": float(receita_venda),
                "custo_transporte_total_venda": float(custo_transporte_venda),
                "custo_producao_itens_vendidos": float(custo_producao_dos_vendidos),
                "lucro_liquido_desta_venda": float(lucro_liquido_da_venda),
                "saldo_final_jogador": float(jogador_partida_obj.saldo),
                "estoque_final_do_produto_vendido": estoque_do_produto_demandado.quantidade
            })
        
    rodada_atual.resultados = resultados_rodada
    rodada_atual.save()

# Função placeholder para buscar custo de transporte (será implementada com o novo modelo)
def buscar_custo_transporte(origem: str, destino: str, produto: Produto) -> Decimal | None:
    # Esta função irá consultar o novo modelo CustoTransporte
    # Por enquanto, retorna um valor fixo ou None para forçar o fallback
    # Exemplo:
    # from .models import CustoTransporte (você vai criar este modelo)
    # try:
    #     custo_obj = CustoTransporte.objects.get(empresa_origem=origem, local_destino=destino, produto=produto)
    #     return custo_obj.custo_unitario
    # except CustoTransporte.DoesNotExist:
    #     return None
    return Decimal('3.50') # Placeholder

# ... (avançar_rodada permanece estruturalmente o mesmo, mas agora chama a `processar_rodada_atual` atualizada) ...
@transaction.atomic
def avancar_rodada(partida: Partida) -> Rodada | None:
    rodada_atual = Rodada.objects.filter(partida=partida, ativo=True).order_by('-numero').first()

    if not rodada_atual:
        numero_nova_rodada = 1
    else:
        if not todos_jogadores_decidiram(rodada_atual): # Esta função pode precisar de ajuste para o novo fluxo de "decisão de produção"
            return None 

        processar_rodada_atual(rodada_atual) # Processa a rodada que está terminando

        rodada_atual.ativo = False
        rodada_atual.data_fim = timezone.now()
        rodada_atual.save()
        numero_nova_rodada = rodada_atual.numero + 1
    
    nova_rodada = Rodada.objects.create(
        partida=partida,
        numero=numero_nova_rodada,
        ativo=True,
        data_inicio=timezone.now()
    )
    
    # Inicialização de estoque para jogadores na primeira rodada ou ao entrar na partida
    # Se for a primeira rodada (numero_nova_rodada == 1), pode ser um bom momento para dar um estoque inicial.
    if numero_nova_rodada == 1:
        produtos_disponiveis = Produto.objects.all()
        jogadores_da_partida = JogadorPartida.objects.filter(partida=partida)
        for jogador_p in jogadores_da_partida:
            for produto_base in produtos_disponiveis:
                EstoqueJogador.objects.update_or_create( # Usar update_or_create para evitar duplicados se rodar de novo
                    jogador_partida=jogador_p,
                    produto=produto_base,
                    defaults={'quantidade': 50} # Ex: Dar 50 unidades de cada produto inicialmente
                )
                # Também zerar/definir saldo inicial do JogadorPartida aqui se for o caso
                # jogador_p.saldo = Decimal('10000.00') # Ex: Saldo inicial
                # jogador_p.save()


    return nova_rodada